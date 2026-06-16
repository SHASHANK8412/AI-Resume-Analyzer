<<<<<<< HEAD
# 🤖 AI Resume Analyzer & ATS Checker

A powerful AI-powered resume analysis tool that compares your resume against a job description, gives you an ATS match score, identifies skill gaps, and generates personalized interview questions — all powered by **Groq LLM**.

---

## ✨ Features

- 📄 **PDF & DOCX Support** — Extracts text from both resume formats
- 🎯 **ATS Match Score** — Visual circular gauge score (0–100) with color-coded rating
- ✅ **Matched Skills** — Shows skills found in your resume with evidence
- ❌ **Missing Skills** — Highlights skills required by the JD that are absent
- 🌟 **Core Strengths** — Identifies your strongest profile points
- 💡 **Improvement Plan** — Personalized, actionable suggestions to boost your ATS score
- 🎤 **Interview Prep** — AI-generated technical & behavioral questions based on the JD
- 📊 **Summary Stats** — Quick count of matched skills, missing skills, and interview questions

---

## 🖥️ UI Preview

| Section | Description |
|---|---|
| **Hero Banner** | Dark gradient header with feature badges |
| **Score Card** | SVG circular gauge with color-coded label |
| **Stats Row** | 3-column grid: Matched / Missing / Interview Qs |
| **Tabbed Results** | What You Have · What You Lack · Improvements · Interview Prep · Resume Preview |
| **Skill Tags** | Pill-shaped colored tags for matched/missing skills |
| **Info Strip** | Footer feature summary |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SHASHANK8412/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Get a free API key at [console.groq.com](https://console.groq.com)

### 5. Run the app

```bash
python main.py
```

Open your browser at **http://127.0.0.1:7860**

---

## 📁 Project Structure

```
AI-Resume-Analyzer/
├── main.py           # Gradio UI & app entry point
├── analyzer.py       # LLM + heuristic resume analysis logic
├── parser.py         # PDF & DOCX text extraction
├── requirements.txt  # Python dependencies
├── .env              # API keys (not committed)
└── .gitignore
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI** | [Gradio](https://gradio.app) with custom CSS & HTML |
| **LLM** | [Groq](https://groq.com) — `llama-3.1-8b-instant` |
| **PDF Parsing** | [pdfplumber](https://github.com/jsvine/pdfplumber) |
| **DOCX Parsing** | [python-docx](https://python-docx.readthedocs.io) |
| **Env Config** | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

## ⚙️ How It Works

1. **Text Extraction** — `parser.py` extracts raw text from the uploaded PDF or DOCX
2. **Heuristic Analysis** — Keyword tokenization & frequency matching as a fast baseline
3. **LLM Analysis** — Groq LLM performs semantic matching, identifies evidence, and generates personalized feedback
4. **Fallback** — If the Groq API is unavailable, the heuristic analysis is used automatically
5. **Rich UI** — Results are rendered as styled HTML cards, skill tags, and a circular SVG gauge

---

## 📝 License

MIT License — feel free to use, modify, and distribute.

---

## 🙋 Author

**Shashank** — [GitHub](https://github.com/SHASHANK8412)
=======
# AI-Resume-Analyzer
>>>>>>> 4cac4384c636905079219405d4f17fd5b797b30a
