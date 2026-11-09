import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Find the .env file in the backend folder
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


def analyze_script_with_ai(script_text: str) -> str:
    """Send the script to Gemini for a smart AI analysis."""
    if client is None:
        return "Error: GEMINI_API_KEY is not set in the backend/.env file."

    prompt = f"""
    You are an expert script doctor and film producer. Read the following screenplay.
    Provide a professional analysis with these sections:
    1. PLOT SUMMARY: A brief, engaging 3-sentence summary of the story.
    2. PLOT HOLES: Point out any logical inconsistencies or unanswered questions.
    3. WEAK DIALOGUE: Point out any lines that sound unnatural or "on the nose".
    4. CHARACTER FEEDBACK: Are the character motivations clear?

    Keep your feedback constructive, clear, and easy for a beginner to understand.
    Do not invent details that are not in the script.

    SCREENPLAY:
    {script_text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"