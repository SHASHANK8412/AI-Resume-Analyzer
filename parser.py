import os

import pdfplumber
from docx import Document


def extract_text_from_pdf(file_path):
	text = ""
	with pdfplumber.open(file_path) as pdf:
		for page in pdf.pages:
			page_text = page.extract_text()
			if page_text:
				text += page_text + "\n"
	return text.strip()


def extract_text_from_docx(file_path):
	doc = Document(file_path)
	text = ""
	for paragraph in doc.paragraphs:
		text += paragraph.text + "\n"
	return text.strip()


def extract_resume_text(file_path):
	ext = os.path.splitext(file_path)[1].lower()

	if ext == ".pdf":
		return extract_text_from_pdf(file_path)
	elif ext == ".docx":
		return extract_text_from_docx(file_path)
	else:
		raise ValueError(f"Unsupported file type: {ext}")
