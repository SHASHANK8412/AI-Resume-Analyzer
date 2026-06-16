import os

import gradio as gr
from dotenv import load_dotenv

from analyzer import analyze_resume
from parser import extract_resume_text


load_dotenv()


def _format_bullets(items):
	if not items:
		return "- None identified."
	return "\n".join(f"- {item}" for item in items)


def _resolve_file_path(uploaded_file):
	if uploaded_file is None:
		return None
	if isinstance(uploaded_file, str):
		return uploaded_file
	return getattr(uploaded_file, "name", None) or getattr(uploaded_file, "path", None)


def _score_color(score):
	if score >= 80:
		return "#10b981", "#d1fae5", "Excellent Match 🎉"
	elif score >= 60:
		return "#f59e0b", "#fef3c7", "Good Match 👍"
	elif score >= 40:
		return "#ef6c2f", "#ffedd5", "Fair Match ⚠️"
	else:
		return "#ef4444", "#fee2e2", "Needs Work 🔧"


def _skill_tags_html(items, color="#ef6c2f", bg="#ffedd5"):
	if not items:
		return "<p style='color:#94a3b8; font-style:italic;'>None identified.</p>"
	tags = ""
	for item in items:
		tags += f"""<span style="
			display:inline-block;
			background:{bg};
			color:{color};
			border:1px solid {color}33;
			border-radius:20px;
			padding:4px 14px;
			margin:4px 4px;
			font-size:13px;
			font-weight:500;
			line-height:1.4;
		">{item}</span>"""
	return f"<div style='display:flex;flex-wrap:wrap;gap:2px;'>{tags}</div>"


def _card_html(title, icon, content_html, accent="#ef6c2f"):
	return f"""
	<div style="
		background: white;
		border-radius: 16px;
		border: 1px solid #e2e8f0;
		padding: 20px 24px;
		margin-bottom: 16px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.04);
	">
		<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
			<span style="font-size:22px;">{icon}</span>
			<h3 style="margin:0;font-size:16px;font-weight:700;color:#1e293b;">{title}</h3>
		</div>
		{content_html}
	</div>
	"""


def _bullet_list_html(items, color="#475569"):
	if not items:
		return "<p style='color:#94a3b8; font-style:italic;'>None identified.</p>"
	rows = ""
	for item in items:
		rows += f"""
		<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid #f1f5f9;">
			<span style="color:#ef6c2f;font-size:16px;margin-top:1px;flex-shrink:0;">›</span>
			<span style="color:{color};font-size:14px;line-height:1.6;">{item}</span>
		</div>"""
	return f"<div>{rows}</div>"


def _question_list_html(items):
	if not items:
		return "<p style='color:#94a3b8; font-style:italic;'>None identified.</p>"
	rows = ""
	for i, item in enumerate(items, 1):
		rows += f"""
		<div style="
			display:flex;align-items:flex-start;gap:12px;
			padding:12px 14px;
			background:#f8fafc;
			border-radius:10px;
			margin-bottom:8px;
			border-left:3px solid #6366f1;
		">
			<span style="
				background:#6366f1;color:white;
				border-radius:50%;width:22px;height:22px;
				display:flex;align-items:center;justify-content:center;
				font-size:11px;font-weight:700;flex-shrink:0;margin-top:1px;
			">{i}</span>
			<span style="color:#334155;font-size:14px;line-height:1.6;">{item}</span>
		</div>"""
	return f"<div>{rows}</div>"


def run_analysis(uploaded_file, job_description):
	file_path = _resolve_file_path(uploaded_file)
	if not file_path:
		raise gr.Error("Please upload a PDF or DOCX resume.")

	if not job_description or not job_description.strip():
		raise gr.Error("Please paste a job description.")

	resume_text = extract_resume_text(file_path)
	if not resume_text:
		raise gr.Error("No text could be extracted from the resume file.")

	resolved_api_key = os.getenv("GROQ_API_KEY")
	result = analyze_resume(resume_text, job_description, resolved_api_key)

	score = result["ats_score"]
	matched = result.get("matched_skills", [])
	missing = result.get("missing_skills", [])
	strengths = result.get("strengths", [])
	feedback = result.get("feedback", [])
	questions = result.get("interview_questions", [])

	accent_color, accent_bg, label = _score_color(score)

	# Circular gauge SVG
	radius = 54
	circumference = 2 * 3.14159 * radius
	dash = (score / 100) * circumference
	gap = circumference - dash

	score_html = f"""
	<div style="
		background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
		border-radius: 20px;
		border: 1px solid #e2e8f0;
		padding: 28px 24px;
		text-align: center;
		box-shadow: 0 4px 20px rgba(0,0,0,0.06);
		margin-bottom: 20px;
	">
		<p style="margin:0 0 16px 0;font-size:13px;font-weight:600;color:#64748b;letter-spacing:0.08em;text-transform:uppercase;">ATS Match Score</p>
		<div style="position:relative;display:inline-block;width:140px;height:140px;">
			<svg width="140" height="140" viewBox="0 0 140 140" style="transform:rotate(-90deg);">
				<circle cx="70" cy="70" r="{radius}" fill="none" stroke="#e2e8f0" stroke-width="12"/>
				<circle cx="70" cy="70" r="{radius}" fill="none" stroke="{accent_color}" stroke-width="12"
					stroke-dasharray="{dash:.1f} {gap:.1f}"
					stroke-linecap="round"
					style="transition:stroke-dasharray 1s ease;"/>
			</svg>
			<div style="
				position:absolute;top:50%;left:50%;
				transform:translate(-50%,-50%);
				text-align:center;
			">
				<div style="font-size:32px;font-weight:800;color:{accent_color};line-height:1;">{score}</div>
				<div style="font-size:11px;color:#94a3b8;font-weight:500;">/100</div>
			</div>
		</div>
		<div style="margin-top:14px;">
			<span style="
				background:{accent_bg};
				color:{accent_color};
				border:1px solid {accent_color}44;
				border-radius:20px;
				padding:5px 18px;
				font-size:14px;
				font-weight:600;
			">{label}</span>
		</div>
	</div>

	<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:4px;">
		<div style="background:#f0fdf4;border-radius:12px;padding:14px;text-align:center;border:1px solid #bbf7d0;">
			<div style="font-size:22px;font-weight:800;color:#10b981;">{len(matched)}</div>
			<div style="font-size:11px;color:#059669;font-weight:600;margin-top:2px;">Matched Skills</div>
		</div>
		<div style="background:#fff7ed;border-radius:12px;padding:14px;text-align:center;border:1px solid #fed7aa;">
			<div style="font-size:22px;font-weight:800;color:#f97316;">{len(missing)}</div>
			<div style="font-size:11px;color:#ea580c;font-weight:600;margin-top:2px;">Missing Skills</div>
		</div>
		<div style="background:#f5f3ff;border-radius:12px;padding:14px;text-align:center;border:1px solid #ddd6fe;">
			<div style="font-size:22px;font-weight:800;color:#7c3aed;">{len(questions)}</div>
			<div style="font-size:11px;color:#6d28d9;font-weight:600;margin-top:2px;">Interview Qs</div>
		</div>
	</div>
	"""

	matched_html = (
		_card_html("Matched Skills & Evidence", "✅",
			_skill_tags_html(matched, "#059669", "#f0fdf4"), "#10b981") +
		_card_html("Core Strengths", "🌟",
			_bullet_list_html(strengths, "#374151"), "#f59e0b")
	)

	missing_html = _card_html(
		"Missing Skills", "❌",
		_skill_tags_html(missing, "#dc2626", "#fef2f2"), "#ef4444"
	)

	improve_html = _card_html(
		"Actionable Improvement Plan", "💡",
		_bullet_list_html(feedback, "#374151"), "#ef6c2f"
	)

	qa_html = _card_html(
		"Interview Preparation Questions", "🎯",
		_question_list_html(questions), "#6366f1"
	)

	preview_text = resume_text[:3000]

	return score_html, matched_html, missing_html, improve_html, qa_html, preview_text


# ── CSS ──────────────────────────────────────────────────────────────────────

CSS = """
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
	--bg:       #f1f5f9;
	--surface:  #ffffff;
	--text:     #1e293b;
	--muted:    #64748b;
	--accent:   #ef6c2f;
	--accent2:  #6366f1;
	--border:   #e2e8f0;
	--radius:   16px;
	--shadow:   0 4px 24px rgba(0,0,0,0.07);
}

* { font-family: 'Inter', system-ui, sans-serif !important; box-sizing: border-box; }

body, .gradio-container {
	background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #ede9fe 100%) !important;
	min-height: 100vh;
}

/* ── Main container ── */
.main-wrap {
	max-width: 1280px !important;
	margin: 0 auto !important;
	padding: 0 16px !important;
}

/* ── Hero banner ── */
.hero-banner {
	background: linear-gradient(135deg, #1e293b 0%, #0f172a 60%, #1e1b4b 100%);
	border-radius: 24px;
	padding: 40px 48px;
	margin-bottom: 28px;
	position: relative;
	overflow: hidden;
	box-shadow: 0 8px 40px rgba(15,23,42,0.25);
}

.hero-banner::before {
	content: '';
	position: absolute;
	top: -60px; right: -60px;
	width: 280px; height: 280px;
	background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%);
	border-radius: 50%;
}

.hero-banner::after {
	content: '';
	position: absolute;
	bottom: -40px; left: 30%;
	width: 200px; height: 200px;
	background: radial-gradient(circle, rgba(239,108,47,0.2) 0%, transparent 70%);
	border-radius: 50%;
}

.hero-title {
	font-size: 36px !important;
	font-weight: 800 !important;
	color: #ffffff !important;
	margin: 0 0 10px 0 !important;
	line-height: 1.2 !important;
	position: relative; z-index: 1;
}

.hero-title span { color: #fb923c; }

.hero-sub {
	font-size: 15px !important;
	color: #94a3b8 !important;
	margin: 0 !important;
	max-width: 680px;
	line-height: 1.7 !important;
	position: relative; z-index: 1;
}

.hero-badges {
	display: flex;
	gap: 10px;
	margin-top: 20px;
	flex-wrap: wrap;
	position: relative; z-index: 1;
}

.hero-badge {
	background: rgba(255,255,255,0.1);
	border: 1px solid rgba(255,255,255,0.15);
	border-radius: 20px;
	padding: 5px 14px;
	font-size: 12px;
	color: #cbd5e1;
	font-weight: 500;
}

/* ── Panel cards ── */
.input-panel, .output-panel {
	background: var(--surface);
	border-radius: 20px;
	border: 1px solid var(--border);
	padding: 24px;
	box-shadow: var(--shadow);
}

/* ── Section labels ── */
.section-label {
	font-size: 11px !important;
	font-weight: 700 !important;
	letter-spacing: 0.1em !important;
	text-transform: uppercase !important;
	color: var(--muted) !important;
	margin-bottom: 8px !important;
}

/* ── Gradio overrides ── */
label.svelte-1b6s6s, .label-wrap span {
	font-size: 13px !important;
	font-weight: 600 !important;
	color: #374151 !important;
}

.gr-button-primary, button[variant="primary"] {
	background: linear-gradient(135deg, #ef6c2f 0%, #dc4e0a 100%) !important;
	border: none !important;
	border-radius: 12px !important;
	font-size: 15px !important;
	font-weight: 700 !important;
	padding: 14px 28px !important;
	color: white !important;
	box-shadow: 0 4px 14px rgba(239,108,47,0.4) !important;
	transition: all 0.2s ease !important;
	width: 100% !important;
}

.gr-button-primary:hover, button[variant="primary"]:hover {
	transform: translateY(-1px) !important;
	box-shadow: 0 6px 20px rgba(239,108,47,0.5) !important;
}

/* File upload */
.gr-file-upload, [data-testid="file-upload"] {
	border: 2px dashed #cbd5e1 !important;
	border-radius: 14px !important;
	background: #f8fafc !important;
	transition: border-color 0.2s !important;
}

.gr-file-upload:hover, [data-testid="file-upload"]:hover {
	border-color: #ef6c2f !important;
	background: #fff7ed !important;
}

/* Textbox */
textarea, .gr-textbox textarea {
	border-radius: 12px !important;
	border: 1.5px solid #e2e8f0 !important;
	font-size: 14px !important;
	color: #374151 !important;
	background: #f8fafc !important;
	transition: border-color 0.2s !important;
	resize: vertical !important;
}

textarea:focus, .gr-textbox textarea:focus {
	border-color: #ef6c2f !important;
	background: #ffffff !important;
	box-shadow: 0 0 0 3px rgba(239,108,47,0.12) !important;
	outline: none !important;
}

/* Tabs */
.tab-nav button {
	font-size: 13px !important;
	font-weight: 600 !important;
	border-radius: 10px 10px 0 0 !important;
	padding: 10px 18px !important;
	color: #64748b !important;
	border: none !important;
	background: transparent !important;
	transition: all 0.2s !important;
}

.tab-nav button.selected {
	color: #ef6c2f !important;
	border-bottom: 2px solid #ef6c2f !important;
	background: transparent !important;
}

/* Accordion */
.gr-accordion {
	border-radius: 12px !important;
	border: 1px solid #e2e8f0 !important;
	overflow: hidden !important;
}

/* Footer info strip */
.info-strip {
	display: flex;
	gap: 24px;
	flex-wrap: wrap;
	justify-content: center;
	padding: 20px;
	background: white;
	border-radius: 16px;
	border: 1px solid #e2e8f0;
	margin-top: 24px;
	box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.info-item {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	color: #64748b;
	font-weight: 500;
}

.info-dot {
	width: 8px; height: 8px;
	border-radius: 50%;
	background: #ef6c2f;
	flex-shrink: 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Responsive */
@media (max-width: 768px) {
	.hero-banner { padding: 28px 24px; }
	.hero-title { font-size: 26px !important; }
}
"""

HERO_HTML = """
<div class="hero-banner">
  <h1 class="hero-title">AI Resume Analyzer <span>&amp;</span> ATS Checker</h1>
  <p class="hero-sub">
    Upload your resume, paste a job description, and get an instant AI-powered ATS match score,
    skill gap analysis, personalized feedback, and interview prep questions — powered by Groq LLM.
  </p>
  <div class="hero-badges">
    <span class="hero-badge">⚡ Powered by Groq</span>
    <span class="hero-badge">📄 PDF &amp; DOCX Support</span>
    <span class="hero-badge">🎯 ATS Score</span>
    <span class="hero-badge">💡 Skill Gap Analysis</span>
    <span class="hero-badge">🎤 Interview Prep</span>
  </div>
</div>
"""

INFO_STRIP_HTML = """
<div class="info-strip">
  <div class="info-item"><div class="info-dot"></div>Extracts text from PDF &amp; DOCX resumes</div>
  <div class="info-item"><div class="info-dot"></div>Semantic keyword matching via LLM</div>
  <div class="info-item"><div class="info-dot"></div>ATS-style match score (0–100)</div>
  <div class="info-item"><div class="info-dot"></div>Personalized improvement suggestions</div>
  <div class="info-item"><div class="info-dot"></div>AI-generated interview questions</div>
</div>
"""

# ── Gradio App ────────────────────────────────────────────────────────────────

THEME = gr.themes.Base(
	primary_hue=gr.themes.colors.orange,
	secondary_hue=gr.themes.colors.indigo,
	neutral_hue=gr.themes.colors.slate,
	font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
	font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
).set(
	body_background_fill="transparent",
	block_background_fill="white",
	block_border_width="1px",
	block_border_color="#e2e8f0",
	block_radius="16px",
	block_shadow="0 2px 8px rgba(0,0,0,0.05)",
	button_primary_background_fill="linear-gradient(135deg, #ef6c2f, #dc4e0a)",
	button_primary_background_fill_hover="linear-gradient(135deg, #f97316, #ef6c2f)",
	button_primary_text_color="white",
	button_primary_border_color="transparent",
)

with gr.Blocks(title="AI Resume Analyzer & ATS Checker") as demo:

	gr.HTML(HERO_HTML)

	with gr.Row(equal_height=False):
		# ── LEFT: Inputs ──────────────────────────────────────────────────────
		with gr.Column(scale=4, min_width=320):
			gr.Markdown("### 📂 Upload & Configure", elem_classes="section-label")

			resume_file = gr.File(
				label="Resume File",
				file_types=[".pdf", ".docx"],
				type="filepath",
				height=120,
			)

			job_description = gr.Textbox(
				label="Job Description",
				lines=16,
				max_lines=30,
				placeholder="Paste the full job description here...\n\nInclude requirements, responsibilities, and preferred qualifications for the best analysis.",
			)

			analyze_button = gr.Button(
				"🔍  Analyze Resume",
				variant="primary",
				size="lg",
			)

			gr.HTML("""
			<div style="
				background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
				border: 1px solid #bbf7d0;
				border-radius: 12px;
				padding: 14px 16px;
				margin-top: 4px;
			">
				<p style="margin:0;font-size:12px;color:#065f46;font-weight:500;line-height:1.6;">
					💡 <strong>Tip:</strong> For best results, paste the complete job description including
					required skills, responsibilities, and qualifications. The more detail, the more accurate the analysis.
				</p>
			</div>
			""")

		# ── RIGHT: Outputs ────────────────────────────────────────────────────
		with gr.Column(scale=6, min_width=400):
			gr.Markdown("### 📊 Analysis Results", elem_classes="section-label")

			score_output = gr.HTML(
				value="""
				<div style="
					background: linear-gradient(135deg, #f8fafc, #f1f5f9);
					border-radius: 20px;
					border: 2px dashed #e2e8f0;
					padding: 48px 24px;
					text-align: center;
					color: #94a3b8;
				">
					<div style="font-size:48px;margin-bottom:12px;">📋</div>
					<p style="margin:0;font-size:15px;font-weight:600;color:#64748b;">Upload a resume &amp; paste a job description</p>
					<p style="margin:8px 0 0 0;font-size:13px;color:#94a3b8;">Your ATS score and analysis will appear here</p>
				</div>
				"""
			)

			with gr.Tabs() as result_tabs:
				with gr.Tab("✅ What You Have", id="have"):
					have_output = gr.HTML(
						value="<p style='color:#94a3b8;text-align:center;padding:24px;font-size:14px;'>Run analysis to see matched skills and strengths.</p>"
					)

				with gr.Tab("❌ What You Lack", id="lack"):
					lack_output = gr.HTML(
						value="<p style='color:#94a3b8;text-align:center;padding:24px;font-size:14px;'>Run analysis to see missing skills.</p>"
					)

				with gr.Tab("💡 Improvements", id="improve"):
					improve_output = gr.HTML(
						value="<p style='color:#94a3b8;text-align:center;padding:24px;font-size:14px;'>Run analysis to see improvement suggestions.</p>"
					)

				with gr.Tab("🎯 Interview Prep", id="qa"):
					qa_output = gr.HTML(
						value="<p style='color:#94a3b8;text-align:center;padding:24px;font-size:14px;'>Run analysis to see interview questions.</p>"
					)

				with gr.Tab("📄 Resume Preview", id="preview"):
					resume_preview = gr.Textbox(
						label="Extracted Text (first 3000 chars)",
						lines=14,
						interactive=False,
						placeholder="Extracted resume text will appear here after analysis...",
					)

	gr.HTML(INFO_STRIP_HTML)

	analyze_button.click(
		fn=run_analysis,
		inputs=[resume_file, job_description],
		outputs=[score_output, have_output, lack_output, improve_output, qa_output, resume_preview],
	)


if __name__ == "__main__":
	demo.launch(css=CSS, theme=THEME)
