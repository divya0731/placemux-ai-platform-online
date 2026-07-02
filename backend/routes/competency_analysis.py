"""
routes/competency_analysis.py — Per-competency score breakdown
==============================================================
Provides:
  GET  /api/competency-analysis/{candidate_id}  — HTTP route (FastAPI)
  get_competency_analysis(candidate_id, db)      — internal helper for score.py

The helper function is separated from the route handler so that score.py can
call it directly without going through FastAPI's Depends() injection machinery.

Return shape (both route and helper):
  {
    "<competency_id>": {
      "skill":            "<human-readable skill name>",
      "total_questions":  int,
      "correct_answers":  int,
      "score":            float  # 0-100
    },
    ...
  }

Keys are canonical competency_ids (e.g. "CSE001", "ECE002") so that
recommendations.py can directly look up candidate_vec[comp_id].
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.response import Response
from models.questions import Question
import json
import os

router = APIRouter(prefix="/api")

# ── Competency metadata lookup ────────────────────────────────────────────────
# Map competency_id → skill name (loaded once at startup)
_COMPETENCIES_MAP: dict[str, str] = {}
_COMPETENCIES_FILE = os.path.join(
    os.path.dirname(__file__),   # routes/
    "..", "..",                   # project root
    "ontology", "competencies.json",
)
_COMPETENCIES_FILE = os.path.normpath(_COMPETENCIES_FILE)

try:
    with open(_COMPETENCIES_FILE, "r", encoding="utf-8") as _f:
        _data = json.load(_f)
        _COMPETENCIES_MAP = {item["competency_id"]: item["skill"] for item in _data}
except Exception as _e:
    print(f"[competency_analysis] Warning — could not load competencies.json: {_e}")


# ── Internal helper (called directly by score.py) ────────────────────────────

def get_competency_analysis(candidate_id: int, db: Session) -> dict:
    """
    Compute per-competency scores for a candidate from their response history.

    Returns a dict keyed by competency_id:
      {
        "CSE001": {"skill": "Python (Advanced & OOPs)", "total_questions": 5,
                   "correct_answers": 4, "score": 80.0},
        ...
      }

    An empty dict is returned if the candidate has no responses yet.
    """
    joined = (
        db.query(Response, Question)
        .join(Question, Response.question_id == Question.question_id)
        .filter(Response.candidate_id == candidate_id)
        .all()
    )

    if not joined:
        return {}

    result: dict = {}

    for response, question in joined:
        comp_id   = question.competency_id or "UNKNOWN"
        skill_name = _COMPETENCIES_MAP.get(comp_id, comp_id)

        if comp_id not in result:
            result[comp_id] = {
                "skill":           skill_name,
                "total_questions": 0,
                "correct_answers": 0,
            }

        result[comp_id]["total_questions"] += 1
        if response.is_correct:
            result[comp_id]["correct_answers"] += 1

    # Compute percentage score for each competency
    for comp_id in result:
        total   = result[comp_id]["total_questions"]
        correct = result[comp_id]["correct_answers"]
        result[comp_id]["score"] = round((correct / total) * 100.0, 1) if total else 0.0

    return result


# ── HTTP route ────────────────────────────────────────────────────────────────

@router.get("/competency-analysis/{candidate_id}")
def competency_analysis_endpoint(
    candidate_id: int, db: Session = Depends(get_db)
):
    """
    GET /api/competency-analysis/{candidate_id}

    Returns per-competency breakdown keyed by competency_id.
    """
    return get_competency_analysis(candidate_id, db)