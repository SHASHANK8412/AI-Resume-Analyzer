import json
import logging
import os
import re
from collections import Counter

try:
	from groq import Groq
except ImportError:
	Groq = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


STOPWORDS = {
	"a",
	"about",
	"above",
	"after",
	"again",
	"against",
	"all",
	"am",
	"an",
	"and",
	"any",
	"are",
	"as",
	"at",
	"be",
	"because",
	"been",
	"before",
	"being",
	"below",
	"between",
	"both",
	"but",
	"by",
	"can",
	"could",
	"did",
	"do",
	"does",
	"doing",
	"down",
	"during",
	"each",
	"few",
	"for",
	"from",
	"further",
	"had",
	"has",
	"have",
	"having",
	"he",
	"her",
	"here",
	"hers",
	"herself",
	"him",
	"himself",
	"his",
	"how",
	"i",
	"if",
	"in",
	"into",
	"is",
	"it",
	"its",
	"itself",
	"just",
	"me",
	"more",
	"most",
	"my",
	"myself",
	"no",
	"nor",
	"not",
	"of",
	"off",
	"on",
	"once",
	"only",
	"or",
	"other",
	"our",
	"ours",
	"ourselves",
	"out",
	"over",
	"own",
	"same",
	"she",
	"should",
	"so",
	"some",
	"such",
	"than",
	"that",
	"the",
	"their",
	"theirs",
	"them",
	"themselves",
	"then",
	"there",
	"these",
	"they",
	"this",
	"those",
	"through",
	"to",
	"too",
	"under",
	"until",
	"up",
	"very",
	"was",
	"we",
	"were",
	"what",
	"when",
	"where",
	"which",
	"while",
	"who",
	"whom",
	"why",
	"will",
	"with",
	"you",
	"your",
	"yours",
	"yourself",
	"yourselves",
}

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _tokenize(text):
	return re.findall(r"[a-z0-9+#.]+", text.lower())


def _normalise_terms(text):
	tokens = [token for token in _tokenize(text) if len(token) >= 3 and token not in STOPWORDS]
	counts = Counter(tokens)
	ordered = [term for term, _ in counts.most_common(40)]
	return set(ordered), ordered


def _format_list(items):
	if not items:
		return "None identified."
	return "\n".join(f"- {item}" for item in items)


def _truncate(text, limit=14000):
	text = text.strip()
	return text if len(text) <= limit else text[:limit] + "\n..."


def _heuristic_questions(missing_skills):
	topics = missing_skills[:5]
	questions = [
		"Tell me about a project where you had to learn a new tool quickly.",
		"How do you prioritize work when requirements change mid-project?",
	]
	for topic in topics:
		questions.append(f"How have you used {topic} in a real project or workflow?")
	return questions[:5]


def _heuristic_analysis(resume_text, job_description):
	resume_terms, resume_order = _normalise_terms(resume_text)
	job_terms, job_order = _normalise_terms(job_description)

	if not job_terms:
		return {
			"ats_score": 0,
			"matched_skills": [],
			"missing_skills": [],
			"strengths": [],
			"feedback": ["Paste a more detailed job description so the analyzer can compare keywords and responsibilities."],
			"interview_questions": _heuristic_questions([]),
		}

	matched = [term for term in job_order if term in resume_terms]
	missing = [term for term in job_order if term not in resume_terms]
	coverage = len(matched) / max(len(job_terms), 1)
	resume_density = len(matched) / max(len(resume_terms), 1)
	score = int(round(min(1.0, (0.75 * coverage) + (0.25 * resume_density)) * 100))

	strengths = matched[:10]
	feedback = [
		"Mirror the job description language in your summary and top bullet points.",
		"Quantify impact with metrics, scope, or business outcomes where possible.",
	]
	if missing:
		feedback.append(f"Add relevant keywords naturally: {', '.join(missing[:8])}.")
	if score < 50:
		feedback.append("Your resume likely needs stronger keyword alignment with the JD.")
	elif score < 75:
		feedback.append("Good baseline match, but there is room to improve keyword coverage and specificity.")
	else:
		feedback.append("Strong match. Focus on tailoring achievements and making role-specific impact clearer.")

	return {
		"ats_score": score,
		"matched_skills": strengths,
		"missing_skills": missing[:12],
		"strengths": strengths,
		"feedback": feedback,
		"interview_questions": _heuristic_questions(missing),
	}


def _extract_json_object(text):
	text = text.strip()
	if text.startswith("```"):
		text = re.sub(r"^```(?:json)?\s*", "", text)
		text = re.sub(r"\s*```$", "", text)
	return json.loads(text)


def _call_groq_analysis(api_key, resume_text, job_description, heuristic_result):
	if not api_key or Groq is None:
		return None

	client = Groq(api_key=api_key)
	prompt = f"""
You are an expert ATS (Applicant Tracking System) and Senior Technical Recruiter with 15+ years of hiring experience.

Your job is to evaluate how well a candidate's resume matches a given job description.

IMPORTANT RULES:
1. Do NOT rely only on exact keyword matching. Perform semantic matching.
2. Recognize equivalent technologies (e.g., React=React.js, JS=JavaScript, REST APIs=API Development).
3. Consider projects, internships, achievements and experience as evidence. 
4. Never hallucinate. If evidence does not exist, say "Not Found".
5. Evaluate realistic ATS Score (0-100).
6. Include evidence for every matched skill in the output string.
7. Missing skills should ONLY include skills that truly do not appear anywhere in the resume.
8. Suggestions MUST be highly personalized, telling the candidate exactly what keywords to add, rephrase, or highlight to improve their ATS score.
9. Return ONLY valid JSON.

**Output Format (Strict JSON only):**
{{
  "ats_score": number (0-100),
  "matched_skills": array of strings (Format: "Skill Name - Evidence from resume"),
  "missing_skills": array of strings (Only explicitly missing skills from the JD),
  "strengths": array of strings (3-5 impactful profile strengths),
  "feedback": array of strings (3-5 actionable steps to rewrite or add specific sections/keywords to maximize the ATS score),
  "interview_questions": array of strings (5 technical/behavioral questions based on matched skills)
}}

Resume text:
{_truncate(resume_text)}

Job description:
{_truncate(job_description)}
""".strip()

	response = client.chat.completions.create(
		model=DEFAULT_MODEL,
		messages=[
			{"role": "system", "content": "You are a precise resume analysis engine that outputs valid JSON only."},
			{"role": "user", "content": prompt},
		],
		temperature=0.4,
		response_format={"type": "json_object"},
	)
	content = response.choices[0].message.content or "{}"
	return _extract_json_object(content)


def analyze_resume(resume_text, job_description, api_key=None):
	heuristic_result = _heuristic_analysis(resume_text, job_description)
	llm_result = None

	try:
		llm_result = _call_groq_analysis(api_key, resume_text, job_description, heuristic_result)
	except Exception as e:
		logging.error(f"Error calling Groq API: {e}", exc_info=True)
		llm_result = None

	if not llm_result:
		logging.warning("LLM analysis failed or returned empty. Falling back to heuristic analysis.")
		return heuristic_result

	score = llm_result.get("ats_score", heuristic_result["ats_score"])
	
	return {
		"ats_score": score,
		"matched_skills": llm_result.get("matched_skills", heuristic_result["matched_skills"]),
		"missing_skills": llm_result.get("missing_skills", heuristic_result["missing_skills"]),
		"strengths": llm_result.get("strengths", heuristic_result["strengths"]),
		"feedback": llm_result.get("feedback", heuristic_result["feedback"]),
		"interview_questions": llm_result.get("interview_questions", heuristic_result["interview_questions"]),
	}
