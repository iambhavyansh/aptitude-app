"""Main FastAPI application"""
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import secrets
import random
from typing import Optional

from database import get_db
from models import Topic, Question, Quiz, Attempt
from config import ADMIN_PASSWORD, SECRET_KEY

app = FastAPI(title="Aptitude Quiz Platform")

templates = Jinja2Templates(directory="templates")

# Simple session management
ADMIN_SESSIONS = set()

def generate_session_token():
    return secrets.token_urlsafe(32)

def check_admin_session(admin_session: Optional[str] = Cookie(None)):
    if not admin_session or admin_session not in ADMIN_SESSIONS:
        return False
    return True

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(password: str = Form(...)):
    """Handle admin login"""
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")

    session_token = generate_session_token()
    ADMIN_SESSIONS.add(session_token)

    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(key="admin_session", value=session_token, httponly=True)
    return response

@app.get("/admin/logout")
async def admin_logout(admin_session: Optional[str] = Cookie(None)):
    """Logout admin"""
    if admin_session and admin_session in ADMIN_SESSIONS:
        ADMIN_SESSIONS.remove(admin_session)

    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_session")
    return response

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin_session: Optional[str] = Cookie(None)
):
    """Admin dashboard"""
    if not check_admin_session(admin_session):
        return RedirectResponse(url="/admin/login", status_code=303)

    # Get all topics with question counts
    topics = db.query(
        Topic.id,
        Topic.main_tag,
        Topic.sub_tag,
        func.count(Question.id).label('question_count')
    ).join(Question, Topic.sub_tag == Question.sub_tag)\
     .group_by(Topic.id, Topic.main_tag, Topic.sub_tag)\
     .all()

    # Get all quizzes
    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).all()

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "topics": topics,
        "quizzes": quizzes
    })

@app.post("/admin/quiz/create")
async def create_quiz(
    request: Request,
    title: str = Form(...),
    time_limit: int = Form(...),
    marks_correct: float = Form(...),
    marks_wrong: float = Form(0.0),
    show_explanations: bool = Form(False),
    admin_session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Create a new quiz"""
    if not check_admin_session(admin_session):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Parse topic selections from form
    form_data = await request.form()
    topic_selections = {}

    for key, value in form_data.items():
        if key.startswith('topic_'):
            sub_tag = key.replace('topic_', '')
            count = int(value)
            if count > 0:
                topic_selections[sub_tag] = count

    if not topic_selections:
        raise HTTPException(status_code=400, detail="No topics selected")

    # Randomly select questions
    selected_question_ids = []

    for sub_tag, count in topic_selections.items():
        questions = db.query(Question).filter(Question.sub_tag == sub_tag).all()

        if len(questions) < count:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough questions in {sub_tag}. Available: {len(questions)}, Requested: {count}"
            )

        selected = random.sample(questions, count)
        selected_question_ids.extend([q.id for q in selected])

    # Shuffle the final question order
    random.shuffle(selected_question_ids)

    # Generate unique share slug
    share_slug = secrets.token_urlsafe(8)

    # Create quiz
    quiz = Quiz(
        title=title,
        time_limit_minutes=time_limit,
        marks_correct=marks_correct,
        marks_wrong=marks_wrong,
        show_explanations=show_explanations,
        question_ids=selected_question_ids,
        share_slug=share_slug
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return RedirectResponse(
        url=f"/admin/quiz/{quiz.id}/results",
        status_code=303
    )

@app.get("/admin/quiz/{quiz_id}/results", response_class=HTMLResponse)
async def quiz_results(
    request: Request,
    quiz_id: int,
    admin_session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """View quiz results"""
    if not check_admin_session(admin_session):
        return RedirectResponse(url="/admin/login", status_code=303)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get all attempts for this quiz
    attempts = db.query(Attempt)\
        .filter(Attempt.quiz_id == quiz_id)\
        .order_by(Attempt.submitted_at.desc())\
        .all()

    # Calculate time taken for each attempt
    for attempt in attempts:
        if attempt.submitted_at and attempt.started_at:
            delta = attempt.submitted_at - attempt.started_at
            attempt.time_taken_str = str(delta).split('.')[0]  # Remove microseconds
        else:
            attempt.time_taken_str = "In progress"

    share_url = f"{request.url.scheme}://{request.url.netloc}/quiz/{quiz.share_slug}"

    return templates.TemplateResponse("quiz_results.html", {
        "request": request,
        "quiz": quiz,
        "attempts": attempts,
        "share_url": share_url
    })

@app.get("/quiz/{share_slug}", response_class=HTMLResponse)
async def quiz_start(
    request: Request,
    share_slug: str,
    db: Session = Depends(get_db)
):
    """Quiz landing page for participants"""
    quiz = db.query(Quiz).filter(Quiz.share_slug == share_slug).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return templates.TemplateResponse("quiz_start.html", {
        "request": request,
        "quiz": quiz
    })

@app.post("/quiz/{share_slug}/begin")
async def begin_quiz(
    share_slug: str,
    participant_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create attempt and start quiz"""
    quiz = db.query(Quiz).filter(Quiz.share_slug == share_slug).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Create attempt
    attempt = Attempt(
        quiz_id=quiz.id,
        participant_name=participant_name,
        answers={}
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return RedirectResponse(
        url=f"/quiz/{share_slug}/take/{attempt.id}",
        status_code=303
    )

@app.get("/quiz/{share_slug}/take/{attempt_id}", response_class=HTMLResponse)
async def take_quiz(
    request: Request,
    share_slug: str,
    attempt_id: int,
    db: Session = Depends(get_db)
):
    """Quiz taking interface"""
    quiz = db.query(Quiz).filter(Quiz.share_slug == share_slug).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt or attempt.quiz_id != quiz.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.submitted_at:
        return RedirectResponse(url=f"/quiz/{share_slug}/result/{attempt_id}")

    # Get questions
    questions = db.query(Question)\
        .filter(Question.id.in_(quiz.question_ids))\
        .all()

    # Sort questions by the order in quiz.question_ids
    questions_dict = {q.id: q for q in questions}
    ordered_questions = [questions_dict[qid] for qid in quiz.question_ids if qid in questions_dict]

    # Calculate deadline
    deadline = attempt.started_at + timedelta(minutes=quiz.time_limit_minutes)

    return templates.TemplateResponse("take_quiz.html", {
        "request": request,
        "quiz": quiz,
        "attempt": attempt,
        "questions": ordered_questions,
        "deadline": deadline.isoformat()
    })

@app.post("/quiz/{share_slug}/submit/{attempt_id}")
async def submit_quiz(
    request: Request,
    share_slug: str,
    attempt_id: int,
    db: Session = Depends(get_db)
):
    """Submit quiz answers"""
    quiz = db.query(Quiz).filter(Quiz.share_slug == share_slug).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt or attempt.quiz_id != quiz.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.submitted_at:
        raise HTTPException(status_code=400, detail="Already submitted")

    # Parse answers
    form_data = await request.form()
    answers = {}

    for key, value in form_data.items():
        if key.startswith('q_'):
            question_id = int(key.replace('q_', ''))
            answers[question_id] = value

    # Calculate score
    questions = db.query(Question).filter(Question.id.in_(quiz.question_ids)).all()
    questions_dict = {q.id: q for q in questions}

    score = 0.0
    for qid in quiz.question_ids:
        if qid not in questions_dict:
            continue

        question = questions_dict[qid]
        selected = answers.get(qid)

        if selected == question.correct_answer:
            score += quiz.marks_correct
        elif selected:  # Answered but wrong
            score += quiz.marks_wrong  # marks_wrong should be negative or 0

    # Update attempt
    attempt.submitted_at = datetime.utcnow()
    attempt.answers = answers
    attempt.score = score

    db.commit()

    return RedirectResponse(
        url=f"/quiz/{share_slug}/result/{attempt_id}",
        status_code=303
    )

@app.get("/quiz/{share_slug}/result/{attempt_id}", response_class=HTMLResponse)
async def quiz_result(
    request: Request,
    share_slug: str,
    attempt_id: int,
    db: Session = Depends(get_db)
):
    """Show quiz result to participant"""
    quiz = db.query(Quiz).filter(Quiz.share_slug == share_slug).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt or attempt.quiz_id != quiz.id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if not attempt.submitted_at:
        raise HTTPException(status_code=400, detail="Quiz not submitted yet")

    # Get questions with answers
    questions = db.query(Question).filter(Question.id.in_(quiz.question_ids)).all()
    questions_dict = {q.id: q for q in questions}
    ordered_questions = [questions_dict[qid] for qid in quiz.question_ids if qid in questions_dict]

    # Add user's answer to each question
    for q in ordered_questions:
        q.user_answer = attempt.answers.get(q.id)
        q.is_correct = (q.user_answer == q.correct_answer)

    # Calculate time taken
    time_taken = "N/A"
    if attempt.submitted_at and attempt.started_at:
        delta = attempt.submitted_at - attempt.started_at
        time_taken = str(delta).split('.')[0]

    return templates.TemplateResponse("quiz_result.html", {
        "request": request,
        "quiz": quiz,
        "attempt": attempt,
        "questions": ordered_questions,
        "time_taken": time_taken
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
