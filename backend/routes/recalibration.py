from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.questions import Question
from models.response import Response
from ai_engine.calibration import calibrate_item_difficulties

router = APIRouter(prefix="/api")

@router.post("/recalibrate")
def recalibrate_items(db: Session = Depends(get_db)):
    """
    Triggered endpoint to re-estimate item difficulty (b_param) from accumulated
    candidate response data.  Switches from SME-seeded cold-start parameters to
    empirically derived parameters once the response volume is sufficient.

    Minimum responses per item before switching: 10.
    Items with fewer than 10 responses keep their seeded b_param.
    """
    MIN_RESPONSES_PER_ITEM = 10

    # 1. Load all questions
    questions = db.query(Question).all()
    q_map = {q.question_id: q for q in questions}

    # 2. Load all responses, grouped per candidate
    all_responses = db.query(Response).all()

    # Build a per-item response count
    item_response_counts = {}
    for r in all_responses:
        item_response_counts[r.question_id] = item_response_counts.get(r.question_id, 0) + 1

    # 3. Build response matrix (only for items with enough data)
    eligible_items = {
        q_id for q_id, count in item_response_counts.items()
        if count >= MIN_RESPONSES_PER_ITEM and q_id in q_map
    }

    if not eligible_items:
        return {
            "status": "skipped",
            "reason": f"No items have ≥{MIN_RESPONSES_PER_ITEM} responses yet. "
                      f"Current max: {max(item_response_counts.values(), default=0)}",
            "items_recalibrated": 0,
        }

    # Build response matrix grouped by candidate
    candidate_map = {}
    for r in all_responses:
        if r.question_id in eligible_items:
            if r.candidate_id not in candidate_map:
                candidate_map[r.candidate_id] = {}
            candidate_map[r.candidate_id][r.question_id] = r.is_correct

    response_matrix = [
        {"candidate_id": cid, "responses": resp}
        for cid, resp in candidate_map.items()
    ]

    # 4. Run calibration pipeline
    initial_difficulties = {q_id: q_map[q_id].b_param for q_id in eligible_items}
    calibrated = calibrate_item_difficulties(response_matrix, initial_difficulties)

    # 5. Persist updated b_params
    updated = []
    for q_id, new_b in calibrated.items():
        if q_id in q_map:
            old_b = q_map[q_id].b_param
            q_map[q_id].b_param = new_b
            updated.append({
                "question_id": q_id,
                "old_b_param": round(old_b, 3),
                "new_b_param": round(new_b, 3),
                "delta":       round(new_b - old_b, 3),
            })

    db.commit()

    return {
        "status": "success",
        "items_recalibrated": len(updated),
        "calibration_log": updated,
    }
