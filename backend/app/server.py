"""ScriptScope FastAPI backend - step 18b.

Two endpoints:
  GET  /health  - check the server is alive
  POST /analyze - analyse a script and return JSON

FastAPI also auto-generates an interactive docs page at /docs.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
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

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(title="ScriptScope API", version="1.0")


class ScriptInput(BaseModel):
    script: str


@app.get("/health")
def health():
    """A tiny endpoint so we can check the server is up."""
    return {"status": "ok", "service": "scriptscope-backend"}


@app.post("/analyze")
def analyze(payload: ScriptInput):
    """Analyse a script.

    Request body (JSON): {"script": "<the script text>"}
    Response: JSON with language, genres, scenes, characters, errors, score, etc.
    """
    text = payload.script
    if not isinstance(text, str) or text.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="The 'script' field must be a non-empty string.",
        )

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)