"""
routes/questions.py — Adaptive CAT endpoint
=============================================
Implements the full CAT loop:
  1. Tab-switch auto-disqualification check (≥3 → immediate stop)
  2. Fetch all responses for this candidate + join question IRT params
  3. EAP theta estimation
  4. SEM-based stopping rules
  5. Content-balanced item selection (Fisher info + competency balancing)
  6. Exposure-capped random pick from top-N candidates
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.questions import Question
from models.response import Response
from models.proctoring import ProctoringLog
from schemas.assessment import NextQuestionRequest, NextQuestionResponse, SubmitAnswerRequest
from ai_engine.irt import estimate_theta_eap, fisher_information, should_stop
import random

router = APIRouter(prefix="/api")

# ── Content-balancing config ─────────────────────────────────────────────────
# Target fraction of items per cluster (approximate; enforced by penalisation)
CLUSTER_TARGET_FRACTION = 0.5   # at most 50% of items from a single cluster
EXPOSURE_TOP_N = 2              # pick randomly from top-N to spread exposure

# ── Calibration-source threshold ─────────────────────────────────────────────
EMPIRICAL_THRESHOLD = 10        # items need ≥10 responses before b_param is considered empirical


def _parameter_source(question: Question, response_count: int) -> str:
    """Determine whether IRT params are seeded or empirically calibrated."""
    return "empirical" if response_count >= EMPIRICAL_THRESHOLD else "seeded"


@router.get("/questions")
def get_all_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()


@router.get("/question/{question_id}")
def get_question(question_id: str, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/next-question", response_model=NextQuestionResponse)
def get_next_question(req: NextQuestionRequest, db: Session = Depends(get_db)):

    # ── 0. Tab-switch auto-disqualification ───────────────────────────────────
    tab_switches = db.query(ProctoringLog).filter(
        ProctoringLog.candidate_id == req.candidate_id,
        ProctoringLog.event_type == "TAB_SWITCH"
    ).count()

    answered_rows = (
        db.query(Response, Question)
        .join(Question, Response.question_id == Question.question_id)
        .filter(Response.candidate_id == req.candidate_id)
        .all()
    )
    irt_responses = [
        {
            "is_correct": resp.is_correct,
            "a_param":    quest.a_param,
            "b_param":    quest.b_param,
            "c_param":    quest.c_param,
        }
        for resp, quest in answered_rows
    ]
    current_theta, current_sem = estimate_theta_eap(irt_responses)

    if tab_switches >= 3:
        return NextQuestionResponse(
            next_question_id=None,
            question_text=None,
            difficulty=req.current_difficulty,
            options=None,
            competency_id=None,
            cluster_id=None,
            bloom_level=None,
            item_type=None,
            finished=True,
            stop_reason="disqualified_tab_switches",
            current_theta=round(current_theta, 3),
            current_sem=round(current_sem, 3),
            items_answered=len(irt_responses),
            parameter_source="seeded",
        )

    # ── 1. Already answered IDs + cluster distribution ───────────────────────
    answered_ids = {r.question_id for r, _ in answered_rows}

    # Count answered items per cluster for content balancing
    cluster_counts: dict[str, int] = {}
    for _, quest in answered_rows:
        cid = quest.cluster_id or "Unknown"
        cluster_counts[cid] = cluster_counts.get(cid, 0) + 1
    total_answered = len(answered_ids)

    # ── 2. Apply stopping rules ───────────────────────────────────────────────
    stop, stop_reason = should_stop(irt_responses, current_sem)
    if stop:
        return NextQuestionResponse(
            next_question_id=None,
            question_text=None,
            difficulty=req.current_difficulty,
            options=None,
            competency_id=None,
            cluster_id=None,
            bloom_level=None,
            item_type=None,
            finished=True,
            stop_reason=stop_reason,
            current_theta=round(current_theta, 3),
            current_sem=round(current_sem, 3),
            items_answered=total_answered,
            parameter_source="seeded",
        )

    # ── 3. Fetch unanswered questions ─────────────────────────────────────────
    unanswered = db.query(Question).filter(
        ~Question.question_id.in_(list(answered_ids)) if answered_ids else True
    ).all()

    # Filter out items that have exceeded exposure cap
    unanswered = [q for q in unanswered if q.exposure_count < q.exposure_cap]

    if not unanswered:
        return NextQuestionResponse(
            next_question_id=None,
            question_text=None,
            difficulty=req.current_difficulty,
            options=None,
            competency_id=None,
            cluster_id=None,
            bloom_level=None,
            item_type=None,
            finished=True,
            stop_reason="item_pool_exhausted",
            current_theta=round(current_theta, 3),
            current_sem=round(current_sem, 3),
            items_answered=total_answered,
            parameter_source="seeded",
        )

    # ── 4. Content-balanced item selection ────────────────────────────────────
    # Score each item by Fisher information, then apply cluster penalty to
    # items from over-represented clusters (> CLUSTER_TARGET_FRACTION).
    def cluster_penalty(q: Question) -> float:
        if total_answered == 0:
            return 1.0
        cid = q.cluster_id or "Unknown"
        fraction = cluster_counts.get(cid, 0) / total_answered
        # Penalise by 50% if cluster is over-represented
        return 0.5 if fraction > CLUSTER_TARGET_FRACTION else 1.0

    scored = sorted(
        [
            (fisher_information(current_theta, q.a_param, q.b_param, q.c_param) * cluster_penalty(q), q)
            for q in unanswered
        ],
        key=lambda x: x[0],
        reverse=True,
    )

    # Pick randomly from top-N to spread exposure
    top_candidates = [q for _, q in scored[:EXPOSURE_TOP_N]]
    selected = random.choice(top_candidates)

    # Determine if the selected item's params are from seeded or empirical calibration
    # Proxy: count how many responses exist for this item across all candidates
    item_response_count = db.query(Response).filter(
        Response.question_id == selected.question_id
    ).count()
    param_src = _parameter_source(selected, item_response_count)

    # Increment exposure count
    selected.exposure_count = (selected.exposure_count or 0) + 1
    db.commit()

    return NextQuestionResponse(
        next_question_id=selected.question_id,
        question_text=selected.question,
        difficulty=selected.difficulty,
        options=[selected.option_a, selected.option_b,
                 selected.option_c, selected.option_d],
        competency_id=selected.competency_id,
        cluster_id=selected.cluster_id,
        bloom_level=selected.bloom_level,
        item_type=selected.item_type,
        finished=False,
        stop_reason=None,
        current_theta=round(current_theta, 3),
        current_sem=round(current_sem, 3),
        items_answered=total_answered,
        parameter_source=param_src,
    )


@router.post("/submit-answer")
def submit_answer(req: SubmitAnswerRequest, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.question_id == req.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = req.selected_option.upper() == question.correct_answer.upper()

    record = Response(
        candidate_id=req.candidate_id,
        question_id=req.question_id,
        selected_option=req.selected_option,
        is_correct=is_correct,
        difficulty=question.difficulty,
        competency_id=question.competency_id,
        response_time_ms=req.response_time_ms,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "candidate_id": record.candidate_id,
        "question_id": record.question_id,
        "selected_option": record.selected_option,
        "is_correct": record.is_correct,
        "difficulty": record.difficulty,
        "competency_id": record.competency_id,
    }


@router.get("/responses/{candidate_id}")
def get_candidate_responses(candidate_id: int, db: Session = Depends(get_db)):
    return db.query(Response).filter(Response.candidate_id == candidate_id).all()