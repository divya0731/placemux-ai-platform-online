"""
routes/score.py — Scoring, Recommendations, Eval & Fairness endpoints
======================================================================
  POST /api/final-score          → EAP theta → scaled score + percentile
  GET  /api/score/{id}           → retrieve stored score
  GET  /api/recommendations/{id} → ranked roles with explanations
  GET  /api/eval-report          → offline CAT scoring stability metrics
  GET  /api/fairness-report      → inter-group fairness analysis by branch
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.response import Response
from models.questions import Question
from models.candidate import Candidate
from models.candidate_score import CandidateScore
from schemas.assessment import FinalScoreRequest, FinalScoreResponse
from ai_engine.irt import estimate_theta_eap
from ai_engine.recommendations import generate_career_recommendations
from ai_engine.eval_harness import run_harness
from ai_engine.fairness_check import run_fairness_check
from routes.competency_analysis import get_competency_analysis  # plain helper, not the FastAPI route

router = APIRouter(prefix="/api")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _compute_percentile(candidate_score: float, db: Session) -> float:
    """
    Compute the percentile rank of a candidate's scaled score
    among all candidates who have a scored record.
    """
    all_scores = [row.scaled_score for row in db.query(CandidateScore).all()]
    if not all_scores:
        return 50.0
    rank = sum(1 for s in all_scores if s < candidate_score)
    return round((rank / len(all_scores)) * 100.0, 1)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/final-score", response_model=FinalScoreResponse)
def calculate_final_score(req: FinalScoreRequest, db: Session = Depends(get_db)):
    """
    Calculates the final IRT score for a candidate after the CAT session.
    Stores result in candidate_scores table and returns it.
    """
    # 1. Fetch candidate responses joined with question IRT params
    responses = db.query(Response, Question).join(
        Question, Response.question_id == Question.question_id
    ).filter(Response.candidate_id == req.candidate_id).all()

    if not responses:
        return FinalScoreResponse(
            ability_estimate=0.0,
            sem=1.0,
            scaled_score=50.0,
            percentile=50.0,
        )

    # 2. Build IRT response list for EAP
    irt_responses = [
        {
            "is_correct": resp.is_correct,
            "a_param":    quest.a_param,
            "b_param":    quest.b_param,
            "c_param":    quest.c_param,
        }
        for resp, quest in responses
    ]

    # 3. EAP estimation
    theta, sem = estimate_theta_eap(irt_responses)

    # 4. Scale theta [-2.5, 2.5] → [0, 100]
    scaled = ((theta + 2.5) / 5.0) * 100.0
    scaled_score    = round(max(0.0, min(100.0, scaled)), 1)
    ability_estimate = round(theta, 3)
    sem              = round(sem, 3)

    # 5. Persist / update in DB
    existing = db.query(CandidateScore).filter(
        CandidateScore.candidate_id == req.candidate_id
    ).first()
    if existing:
        existing.ability_estimate = ability_estimate
        existing.sem              = sem
        existing.scaled_score     = scaled_score
    else:
        db.add(CandidateScore(
            candidate_id=req.candidate_id,
            ability_estimate=ability_estimate,
            sem=sem,
            scaled_score=scaled_score,
        ))
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # 6. Compute percentile (after commit so this candidate is included)
    percentile = _compute_percentile(scaled_score, db)

    return FinalScoreResponse(
        ability_estimate=ability_estimate,
        sem=sem,
        scaled_score=scaled_score,
        percentile=percentile,
    )


@router.get("/score/{candidate_id}")
def get_candidate_score(candidate_id: int, db: Session = Depends(get_db)):
    score = db.query(CandidateScore).filter(
        CandidateScore.candidate_id == candidate_id
    ).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found for candidate")
    percentile = _compute_percentile(score.scaled_score, db)
    return {
        "candidate_id":    score.candidate_id,
        "ability_estimate": score.ability_estimate,
        "sem":             score.sem,
        "scaled_score":    score.scaled_score,
        "percentile":      percentile,
    }


@router.get("/recommendations/{candidate_id}")
def get_recommendations(candidate_id: int, db: Session = Depends(get_db)):
    """
    Returns ranked career role recommendations with match percentages,
    strength/gap analysis, and per-role explanations.
    """
    # 1. Fetch or compute final score
    score = db.query(CandidateScore).filter(
        CandidateScore.candidate_id == candidate_id
    ).first()
    if not score:
        try:
            req = FinalScoreRequest(candidate_id=candidate_id)
            calculate_final_score(req, db)
            score = db.query(CandidateScore).filter(
                CandidateScore.candidate_id == candidate_id
            ).first()
        except Exception:
            raise HTTPException(
                status_code=404,
                detail="Please complete the test to generate matches",
            )
        if not score:
            raise HTTPException(status_code=404, detail="Score record missing")

    # 2. Fetch competency breakdown
    competency_scores = get_competency_analysis(candidate_id, db)

    # 3. Generate ranked matches
    matches = generate_career_recommendations(score.ability_estimate, competency_scores)
    return matches


# ── Evaluation & Fairness Endpoints ──────────────────────────────────────────

@router.get("/eval-report")
def get_eval_report(n_candidates: int = 300, seed: int = 42):
    """
    Runs the offline CAT evaluation harness (synthetic simulation).
    Returns scoring stability metrics: bias, RMSE, SEM coverage, avg items.

    DAY 6 — Evaluation Harness deliverable.
    """
    report = run_harness(n_candidates=n_candidates, seed=seed)
    report["interpretation"] = {
        "bias":           "Mean signed error between estimated and true theta (ideal: ≈0).",
        "rmse":           "Root-mean-square error — lower is better.",
        "sem_coverage_pct": "% of candidates where true theta is within ±1.96 SEM (ideal: ≥95%).",
        "avg_items_per_test": "Average items administered per candidate (shorter = more efficient).",
        "reliability_ok": f"True if avg SEM < threshold ({report['sem_threshold']}).",
    }
    return report


@router.get("/fairness-report")
def get_fairness_report(db: Session = Depends(get_db)):
    """
    Computes inter-group fairness across engineering branches using actual DB scores.
    Applies Cohen's d effect size and EEOC 4/5ths rule.

    DAY 7 — Fairness sanity check deliverable.
    """
    # 1. Fetch all scored candidates joined with their branch
    all_scores = db.query(CandidateScore, Candidate).join(
        Candidate, CandidateScore.candidate_id == Candidate.id
    ).all()

    if not all_scores:
        return {
            "status": "no_data",
            "message": "No scored candidates in the database yet.",
        }

    # 2. Group scaled scores by branch
    scores_by_group: dict[str, list[float]] = {}
    for cs, candidate in all_scores:
        branch = candidate.branch or "Unknown"
        if branch not in scores_by_group:
            scores_by_group[branch] = []
        scores_by_group[branch].append(cs.scaled_score)

    # 3. Remove groups with fewer than 2 members (can't compute statistics)
    scores_by_group = {k: v for k, v in scores_by_group.items() if len(v) >= 2}

    if len(scores_by_group) < 2:
        return {
            "status": "insufficient_data",
            "message": "Need at least 2 branches with ≥2 candidates each for fairness analysis.",
            "current_groups": {k: len(v) for k, v in scores_by_group.items()},
        }

    # 4. Run fairness analysis
    report = run_fairness_check(scores_by_group)
    report["status"] = "success"
    return report