from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.proctoring import ProctoringLog, EVENT_SEVERITY
from schemas.assessment import ProctoringEventRequest, ProctoringVerdictResponse

router = APIRouter(prefix="/api")

# ── Helpers ──────────────────────────────────────────────────────────────────

SEVERITY_WEIGHT = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

def _compute_verdict(logs: list) -> dict:
    """
    Compute a structured integrity verdict from a list of ProctoringLog rows.
    Returns a dict with: risk_score, verdict, violations_count, flag_report, is_disqualified.
    """
    violations_count = len(logs)
    total_weight = sum(SEVERITY_WEIGHT.get(log.severity, 1) for log in logs)

    # Calculate tab switch counts to check for auto-disqualification (limit >= 3)
    tab_switches_count = sum(1 for log in logs if log.event_type == "TAB_SWITCH")
    is_disqualified = tab_switches_count >= 3

    # Risk score: weighted by severity, capped at 100
    risk_score = min(total_weight * 10, 100)

    if risk_score >= 60:
        verdict = "HIGH_RISK"
    elif risk_score >= 30:
        verdict = "MEDIUM_RISK"
    else:
        verdict = "LOW_RISK"

    # Build structured flag report
    flag_report = []
    for log in logs:
        flag_report.append({
            "event_type": log.event_type,
            "severity":   log.severity,
            "timestamp":  log.timestamp.isoformat() if log.timestamp else None,
        })

    return {
        "risk_score":        risk_score,
        "verdict":           verdict,
        "violations_count":  violations_count,
        "flag_report":       flag_report,
        "is_disqualified":   is_disqualified,
    }

# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/proctoring-verdict", response_model=ProctoringVerdictResponse)
def log_proctoring_event(req: ProctoringEventRequest, db: Session = Depends(get_db)):
    # 1. Determine severity for this event type
    severity = EVENT_SEVERITY.get(req.event_type, "MEDIUM")

    # 2. Persist the event
    event = ProctoringLog(
        candidate_id=req.candidate_id,
        event_type=req.event_type,
        severity=severity,
    )
    db.add(event)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # 3. Recompute verdict over all logs for this candidate
    all_logs = (
        db.query(ProctoringLog)
        .filter(ProctoringLog.candidate_id == req.candidate_id)
        .order_by(ProctoringLog.timestamp)
        .all()
    )
    result = _compute_verdict(all_logs)

    return ProctoringVerdictResponse(
        risk_score=result["risk_score"],
        verdict=result["verdict"],
        violations_count=result["violations_count"],
        is_disqualified=result["is_disqualified"],
    )


@router.get("/proctoring-logs/{candidate_id}")
def get_proctoring_logs(candidate_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(ProctoringLog)
        .filter(ProctoringLog.candidate_id == candidate_id)
        .order_by(ProctoringLog.timestamp.desc())
        .all()
    )
    return logs


@router.get("/proctoring-report/{candidate_id}")
def get_proctoring_session_report(candidate_id: int, db: Session = Depends(get_db)):
    """
    Structured session integrity report including per-event flags with severity.
    This is what a human reviewer would see before a go/no-go decision.
    """
    logs = (
        db.query(ProctoringLog)
        .filter(ProctoringLog.candidate_id == candidate_id)
        .order_by(ProctoringLog.timestamp)
        .all()
    )
    result = _compute_verdict(logs)

    # Count events by severity
    severity_breakdown = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for log in logs:
        sev = log.severity if log.severity in severity_breakdown else "MEDIUM"
        severity_breakdown[sev] += 1

    # Human-review routing: if HIGH_RISK, suggest routing to human reviewer
    requires_review = result["verdict"] == "HIGH_RISK"

    return {
        "candidate_id":      candidate_id,
        "verdict":           result["verdict"],
        "risk_score":        result["risk_score"],
        "violations_count":  result["violations_count"],
        "severity_breakdown": severity_breakdown,
        "requires_human_review": requires_review,
        "review_note": (
            "Session flagged for mandatory human review due to HIGH risk score."
            if requires_review
            else "Session passed automated integrity check."
        ),
        "flag_report": result["flag_report"],
    }
