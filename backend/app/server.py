"""ScriptScope FastAPI backend with User Accounts."""
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
    generate_shoot_schedule, extract_text_from_file,
)
from ai.client import analyze_script_with_ai

# Import our new database and auth tools
from database import SessionLocal, User, Script, engine, Base
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from schemas import UserCreate, UserLogin, Token

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
app = FastAPI(title="ScriptScope API", version="1.0")

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# JWT Auth Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


class ScriptInput(BaseModel):
    script: str


# --- Auth Endpoints ---
@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Analysis Endpoints ---
@app.post("/analyze")
def analyze(payload: ScriptInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Rule-based analysis (Saved to history)."""
    text = payload.script
    if not text.strip():
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

    # Save to database!
    new_script = Script(
        user_id=current_user.id,
        content=text,
        score=score,
        tier=tier
    )
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

@app.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch past scripts for the logged-in user."""
    scripts = db.query(Script).filter(Script.user_id == current_user.id).order_by(Script.id.desc()).all()
    return [{"id": s.id, "title": s.title, "score": s.score, "tier": s.tier} for s in scripts]


# --- File Upload & AI (Protected) ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

        # Save to database
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-summary")
def ai_summary(payload: ScriptInput, current_user: User = Depends(get_current_user)):
    text = payload.script
    if not text.strip():
        raise HTTPException(status_code=400, detail="Script is empty.")
    ai_result = analyze_script_with_ai(text)
    return {"ai_analysis": ai_result}


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "scriptscope-backend"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)