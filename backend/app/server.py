"""ScriptScope Flask backend - step 18.

Two endpoints:
  GET  /health  - check the server is alive
  POST /analyze - analyse a script and return JSON
"""
from flask import Flask, request, jsonify

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

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """A tiny endpoint so we can check the server is up."""
    return jsonify({"status": "ok", "service": "scriptscope-backend"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyse a script.

    Request body (JSON): {"script": "<the script text>"}
    Response: JSON with language, genres, scenes, characters, errors, score, etc.
    """
    data = request.get_json(silent=True)
    if not data or "script" not in data:
        return jsonify({"error": 'Send JSON like {"script": "your script text"}'}), 400

    text = data["script"]
    if not isinstance(text, str) or text.strip() == "":
        return jsonify({"error": "The 'script' field must be a non-empty string."}), 400

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

    return jsonify({
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
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)