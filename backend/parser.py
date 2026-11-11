# PDF reading logic + local Ollama AI extraction

import os
import pdfplumber
import instructor
from openai import OpenAI
from backend.schemas import ExamPaperExtractionResult

# Initialize Ollama client using OpenAI-compatible base URL
# Ollama runs locally on port 11434 by default
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # Ollama doesn't require a real API key
    ),
    mode=instructor.Mode.JSON,
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all raw text from a given past paper PDF file."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

def parse_past_paper_with_ai(pdf_path: str, allowed_topics: list[str], model_name: str = "qwen2.5") -> ExamPaperExtractionResult:
    """
    Reads a past paper PDF, injects the dynamic subject scope taxonomy, 
    and uses a local Ollama model to extract structured questions and marks.
    """
    # 1. Get raw text from PDF
    raw_text = extract_text_from_pdf(pdf_path)
    
    # 2. Format allowed topics for the AI prompt
    topics_str = ", ".join([f"'{topic}'" for topic in allowed_topics])
    
    prompt = f"""
    You are an expert academic assistant. Analyze the following past exam paper text.
    Extract every question, its sub-questions, its exact mark allocation, and map it strictly 
    to one of the following allowed curriculum topics: [{topics_str}].
    
    Do not invent or hallucinate new topic names. Every mapped_topic must match one from the allowed list.
    
    Exam Paper Text:
    {raw_text}
    """

    # 3. Call local model via Instructor, enforcing our Pydantic schema
    response = client.chat.completions.create(
        model=model_name,  # e.g., 'qwen2.5' or 'gemma2' running locally in Ollama
        response_model=ExamPaperExtractionResult,
        messages=[
            {"role": "system", "content": "You extract and structure exam paper questions accurately."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # Low temperature for precise, deterministic extraction
    )

    return response