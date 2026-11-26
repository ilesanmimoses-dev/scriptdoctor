"""Analysis wrapper.

Imports the terminal app's functions so both the terminal and the
web API share the exact same logic.
"""
import sys
from pathlib import Path

# Add the terminal folder to Python's search path
_terminal_dir = Path(__file__).resolve().parent.parent.parent / "terminal"
if str(_terminal_dir) not in sys.path:
    sys.path.insert(0, str(_terminal_dir))

# Import the analysis functions we need.
from main import (
    clean_and_split,
    count_genre_matches,
    calculate_percentages,
    find_errors,
    calculate_score,
    choose_comment,
    parse_scenes,
    detect_language,
    count_speeches,
    dialogue_ratio,
    estimate_length,
    explain_simply,
    find_props_and_costumes,
    get_content_rating,
    get_emotion_balance,
    get_budget_and_audience,
    generate_shoot_schedule,
    is_character_cue
)


import io
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(file_bytes, filename):
    """Extract plain text from an uploaded PDF, Word, or TXT file."""
    filename = filename.lower()
    
    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
        
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
        
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8")
        
    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")