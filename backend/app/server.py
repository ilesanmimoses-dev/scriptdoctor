"""ScriptScope FastAPI backend - step 23.

Endpoints:
  GET  /           - serves the frontend page
  GET  /health     - check the server is alive
  POST /analyze    - rule-based analysis
  POST /ai-summary - AI-based analysis (Gemini)
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from analysis import (
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
)

# NEW: Import the AI function
from ai.client import analyze_script_with_ai

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(title="ScriptScope API", version="1.0")


class ScriptInput(BaseModel):
    script: str


@app.get("/")
def index():
    """Serve the frontend page."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    """A tiny endpoint so we can check the server is up."""
    return {"status": "ok", "service": "scriptscope-backend"}


@app.post("/analyze")
def analyze(payload: ScriptInput):
    """Rule-based analysis."""
    text = payload.script
    if not isinstance(text, str) or text.strip() == "":
        raise HTTPException(status_code=400, detail="Script is empty.")

    lines = text.splitlines()
    words = clean_and_split(text)
    counts = count_genre_matches(words)
    percentages = calculate_percentages(counts)
    errors = find_errors(lines)
    score, tier = calculate_score(errors)
    comment = choose_comment(percentages, score)
    scenes = parse_scenes(lines)
    language = detect_language(words)
    speech_counts = count_speeches(lines)
    ratio = dialogue_ratio(lines)
    estimate = estimate_length(words)
    explanation = explain_simply(words, language, scenes, speech_counts, percentages, estimate)
    items = find_props_and_costumes(scenes)

    return {
        "language": language,
        "genres": percentages,
        "scenes": scenes,
        "characters": speech_counts,
        "dialogue_ratio": ratio,
        "estimate": estimate,
        "explanation": explanation,
        "props_and_costumes": items,
        "errors": errors,
        "score": score,
        "tier": tier,
        "comment": comment,
    }


# NEW: The AI endpoint
@app.post("/ai-summary")
def ai_summary(payload: ScriptInput):
    """Uses AI to analyze the script for plot holes and summaries."""
    text = payload.script
    if not text.strip():
        raise HTTPException(status_code=400, detail="Script is empty.")
    
    ai_result = analyze_script_with_ai(text)
    return {"ai_analysis": ai_result}


# Serve the React app in production
DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)