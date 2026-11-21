"""ScriptScope FastAPI backend."""
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
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
    get_content_rating,
    get_emotion_balance,
    get_budget_and_audience,
    generate_shoot_schedule,
    extract_text_from_file, # <--- Make sure this is here
)

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
        "content_rating": get_content_rating(words),
        "emotion_balance": get_emotion_balance(words),
        "budget_and_audience": get_budget_and_audience(words, scenes, speech_counts, get_content_rating(words)),
        "shoot_schedule": generate_shoot_schedule(scenes, days=5),
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Receives an uploaded file, extracts the text, and runs analysis."""
    try:
        contents = await file.read()
        text = extract_text_from_file(contents, file.filename)
        
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
            "content_rating": get_content_rating(words),
            "emotion_balance": get_emotion_balance(words),
            "budget_and_audience": get_budget_and_audience(words, scenes, speech_counts, get_content_rating(words)),
            "shoot_schedule": generate_shoot_schedule(scenes, days=5),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")


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