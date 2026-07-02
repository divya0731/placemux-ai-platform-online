from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models.candidate import Candidate
from models.candidate_score import CandidateScore
from models.proctoring import ProctoringLog
from models.questions import Question
from models.response import Response
from routes.questions import router as question_router
from routes.score import router as score_router
from routes.competency_analysis import router as competency_router
from routes.proctoring import router as proctoring_router
from routes.recalibration import router as recalibration_router

# ── Create all DB tables on startup ────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PlaceMux Adaptive Assessment Platform",
    description="IRT-calibrated CAT with AI proctoring and skills-to-jobs matching.",
    version="1.0.0",
)

# Include all API routers
app.include_router(competency_router)
app.include_router(question_router)
app.include_router(score_router)
app.include_router(proctoring_router)
app.include_router(recalibration_router)

import os
from fastapi.responses import FileResponse

@app.post("/candidate")
def create_candidate(
    name: str,
    email: str,
    branch: str = None,
    college: str = None,
    year_of_study: str = None,
    db: Session = Depends(get_db),
):
    """
    Register a candidate. Returns existing record if email already exists.
    branch       — e.g. CSE | ECE | EEE | IT | MECH
    college      — institution name (used in fairness grouping)
    year_of_study — e.g. '3rd Year', 'Final Year'
    """
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if not candidate:
        candidate = Candidate(
            name=name,
            email=email,
            branch=branch,
            college=college,
            year_of_study=year_of_study,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    else:
        # Update profile fields if provided
        if branch:
            candidate.branch = branch
        if college:
            candidate.college = college
        if year_of_study:
            candidate.year_of_study = year_of_study
        db.commit()

    return {
        "message": "Candidate saved successfully",
        "id":            candidate.id,
        "name":          candidate.name,
        "email":         candidate.email,
        "branch":        candidate.branch,
        "college":       candidate.college,
        "year_of_study": candidate.year_of_study,
    }


# Mount frontend static files — must be last so API routes are matched first
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")