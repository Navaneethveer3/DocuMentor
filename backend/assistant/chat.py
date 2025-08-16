import os
import fitz  # PyMuPDF
import docx
import nltk
import re
import email
from email import policy
from email.parser import BytesParser
import extract_msg
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Only once
nltk.download('punkt')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")

def extract_text(file):
    ext = file.name.lower()

    if ext.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])

    elif ext.endswith(".docx"):
        document = docx.Document(file)
        return "\n".join([para.text for para in document.paragraphs])

    elif ext.endswith(".eml"):
        msg = BytesParser(policy=policy.default).parse(file)
        body = msg.get_body(preferencelist=('plain', 'html'))
        return body.get_content() if body else msg.get_payload()

    elif ext.endswith(".msg"):
        msg = extract_msg.Message(file)
        parts = [
            f"From: {msg.sender}",
            f"Date: {msg.date}",
            f"Subject: {msg.subject}",
            f"\n{msg.body}"
        ]
        return "\n".join(parts)

    else:
        raise ValueError("Unsupported file type")

def split_chunks(text, max_chars=700):
    paragraphs = text.split('\n\n')  # Split by blank lines
    chunks = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) > max_chars:
            chunks.append(current.strip())
            current = ""
        current += para + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def answer_query(query, file):
    text = extract_text(file)

    # Normalize line endings
    normalized_text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Extract structured numbered sections like "38. Pre-Hospitalization..."
    section_pattern = re.compile(r"(\d{1,3}\.\s+[^\n:]+:?-)(.*?)(?=\n\d{1,3}\.\s+[^\n:]+:?-|\Z)", re.DOTALL)
    sections = section_pattern.findall(normalized_text)

    # Combine title + body and build a list
    formatted_sections = [f"{title.strip()}\n{content.strip()}" for title, content in sections]

    if not formatted_sections:
        return {"response": "❌ No structured sections found in the document."}

    # Match query against all section blocks using TF-IDF
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(formatted_sections + [query])
    similarity = cosine_similarity(vectors[-1], vectors[:-1])
    best_idx = similarity.argmax()
    best_section = formatted_sections[best_idx]

    response = (
        "📄 Based on the document, here’s the most relevant information for your query:\n\n"
        f"{best_section.strip()}"
    )

    return {"response": response}