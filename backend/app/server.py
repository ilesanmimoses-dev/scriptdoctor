"""ScriptScope FastAPI backend."""
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from analysis import (
    clean_and_split, count_genre_matches, calculate_percentages, find_errors,
    calculate_score, choose_comment, parse_scenes, detect_language, count_speeches,
    dialogue_ratio, estimate_length, explain_simply, find_props_and_costumes,
    get_content_rating, get_emotion_balance, get_budget_and_audience,
    generate_shoot_schedule, extract_text_from_file, is_character_cue
)
from ai.client import analyze_script_with_ai, generate_coverage_report

from database import SessionLocal, User, Script, Report, engine, Base
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from schemas import UserCreate, UserLogin, Token

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
app = FastAPI(title="ScriptScope API", version="1.0")
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class ScriptInput(BaseModel):
    script: str

@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"access_token": create_access_token(data={"sub": new_user.email}), "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(data={"sub": db_user.email}), "token_type": "bearer"}

@app.post("/analyze")
def analyze(payload: ScriptInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    text = payload.script
    if not text.strip(): raise HTTPException(status_code=400, detail="Script is empty.")

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

    new_script = Script(user_id=current_user.id, content=text, score=score, tier=tier)
    db.add(new_script)
    db.commit()

    return {
        "language": language, "genres": percentages, "scenes": scenes,
        "characters": speech_counts, "dialogue_ratio": ratio, "estimate": estimate,
        "explanation": explanation, "props_and_costumes": items, "errors": errors,
        "score": score, "tier": tier, "comment": comment,
        "content_rating": get_content_rating(words),
        "emotion_balance": get_emotion_balance(words),
        "budget_and_audience": get_budget_and_audience(words, scenes, speech_counts, get_content_rating(words)),
        "shoot_schedule": generate_shoot_schedule(scenes, days=5),
    }

@app.post("/schedule")
def generate_custom_schedule(payload: ScriptInput, days: int = 5, current_user: User = Depends(get_current_user)):
    if not payload.script.strip(): raise HTTPException(status_code=400, detail="Script is empty.")
    scenes = parse_scenes(payload.script.splitlines())
    return {"schedule": generate_shoot_schedule(scenes, days=days)}

@app.post("/explain")
def explain_script_scene_by_scene(payload: ScriptInput, current_user: User = Depends(get_current_user)):
    if not payload.script.strip(): raise HTTPException(status_code=400, detail="Script is empty.")
    scenes = parse_scenes(payload.script.splitlines())
    
    fallback = []
    for i, sc in enumerate(scenes):
        people = []
        for line in sc["lines"]:
            if is_character_cue(line):
                people.append(line.strip())
        
        who = ", ".join(people) if people else "No one speaks in this scene."
        
        fallback.append({
            "scene_number": i + 1,
            "location": f"{sc['interior']}. {sc['location']} - {sc['time']}",
            "who_is_in_it": who,
            "what_happens": f"This scene takes place in the {sc['location'].lower()} and has {sc['word_count']} words of action and dialogue." 
        })
    return {"scenes": fallback}

@app.post("/coverage")
def coverage_report(payload: ScriptInput, current_user: User = Depends(get_current_user)):
    if not payload.script.strip(): raise HTTPException(status_code=400, detail="Script is empty.")
    report = generate_coverage_report(payload.script)
    return {"coverage": report}

@app.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scripts = db.query(Script).filter(Script.user_id == current_user.id).order_by(Script.id.desc()).all()
    return [{"id": s.id, "title": s.title, "score": s.score, "tier": s.tier} for s in scripts]

@app.get("/admin-stats")
def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ADMIN_EMAIL = "test@test.com" 
    if current_user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return {"total_users": db.query(User).count(), "total_scripts": db.query(Script).count()}

@app.post("/report")
def submit_report(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = payload.get("message")
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    new_report = Report(user_id=current_user.id, message=message)
    db.add(new_report)
    db.commit()
    return {"status": "success", "message": "Your report has been submitted."}

@app.get("/admin-reports")
def get_admin_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ADMIN_EMAIL = "test@test.com" 
    if current_user.email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    
    reports = db.query(Report).order_by(Report.id.desc()).all()
    result = []
    for r in reports:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "id": r.id,
            "email": user.email if user else "Unknown",
            "message": r.message,
            "status": r.status
        })
    return result

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        text = extract_text_from_file(await file.read(), file.filename)
        lines = text.splitlines()
        words = clean_and_split(text)
        counts = count_genre_matches(words)
        percentages = calculate_percentages(counts)
        errors = find_errors(lines)
        score, tier = calculate_score(errors)
        scenes = parse_scenes(lines)
        speech_counts = count_speeches(lines)
        
        new_script = Script(user_id=current_user.id, content=text, score=score, tier=tier)
        db.add(new_script)
        db.commit()

        return {
            "language": detect_language(words), "genres": percentages, "scenes": scenes,
            "characters": speech_counts, "dialogue_ratio": dialogue_ratio(lines), 
            "estimate": estimate_length(words), "explanation": explain_simply(words, detect_language(words), scenes, speech_counts, percentages, estimate_length(words)), 
            "props_and_costumes": find_props_and_costumes(scenes), "errors": errors,
            "score": score, "tier": tier, "comment": choose_comment(percentages, score),
            "content_rating": get_content_rating(words), "emotion_balance": get_emotion_balance(words),
            "budget_and_audience": get_budget_and_audience(words, scenes, speech_counts, get_content_rating(words)),
            "shoot_schedule": generate_shoot_schedule(scenes, days=5),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai-summary")
def ai_summary(payload: ScriptInput, current_user: User = Depends(get_current_user)):
    return {"ai_analysis": analyze_script_with_ai(payload.script)}

DIST_DIR = FRONTEND_DIR / "dist"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")

@app.get("/health")
def health(): return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)