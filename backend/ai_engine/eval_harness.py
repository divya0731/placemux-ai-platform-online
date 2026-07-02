"""
Evaluation Harness — ai_engine/eval_harness.py
================================================
Day 6 deliverable: Offline evaluation for scoring stability.

Simulates N synthetic test-takers with known true thetas, runs the full
EAP estimation pipeline after each item, and reports:
  - Bias (mean error between estimated and true theta)
  - RMSE (root-mean-square error)
  - SEM coverage (% of cases where true theta is within ±1.96 SEM of estimate)
  - Mean items administered
  - Reliability: average SEM < SEM_THRESHOLD

Item bank mirrors the seeded production pool (50 items, 4 competencies,
3 difficulty bands) to give realistic convergence characteristics.
"""

import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_engine.irt import (
    probability_correct, estimate_theta_eap,
    should_stop, SEM_THRESHOLD, MAX_ITEMS,
)

# -- Synthetic item bank (mirrors seeded production parameters) ----------------
# 50 items: 4 competencies × (5 Easy + 5 Medium + 5 Hard) + rounding
# a_param: 0.9–1.5 (SME-seeded discrimination)
# b_param: Easy ≈ -1.2 to -1.6 | Medium ≈ -0.2 to 0.2 | Hard ≈ 1.2 to 1.8
# c_param: 0.25 (fixed for 4-option MCQs)

_EASY_ITEMS = [
    (1.2, -1.5), (1.1, -1.3), (1.0, -1.4), (1.3, -1.6), (0.9, -1.0),
    (1.2, -1.5), (1.1, -1.2), (1.0, -1.4), (1.3, -1.6), (1.2, -1.3),
    (1.1, -1.4), (1.0, -1.5), (1.3, -1.2), (0.9, -1.3), (1.2, -1.6),
    (1.1, -1.5), (1.0, -1.3), (1.3, -1.4), (1.2, -1.2), (1.1, -1.6),
]
_MED_ITEMS = [
    (1.0,  0.1), (1.2, -0.1), (1.1,  0.0), (1.3,  0.2), (0.9, -0.2),
    (1.0,  0.0), (1.2,  0.1), (1.1, -0.1), (1.3,  0.2), (1.0, -0.2),
    (1.1,  0.1), (1.0,  0.0), (1.3, -0.1), (0.9,  0.2), (1.2, -0.2),
    (1.0,  0.2), (1.1,  0.1), (1.2,  0.0), (1.3, -0.1), (0.9, -0.2),
]
_HARD_ITEMS = [
    (1.4,  1.4), (1.3,  1.6), (1.2,  1.5), (1.5,  1.7), (1.1,  1.2),
    (1.4,  1.5), (1.3,  1.4), (1.2,  1.6), (1.5,  1.8), (1.1,  1.3),
    (1.4,  1.6), (1.3,  1.5), (1.2,  1.4), (1.5,  1.7), (1.1,  1.2),
    (1.4,  1.3), (1.3,  1.8), (1.2,  1.5), (1.5,  1.6), (1.1,  1.4),
]

ITEMS = [
    {"question_id": f"Q{i+1:03d}", "a_param": a, "b_param": b, "c_param": 0.25}
    for i, (a, b) in enumerate(_EASY_ITEMS + _MED_ITEMS + _HARD_ITEMS)
]

# -- Simulation ---------------------------------------------------------------

def simulate_candidate(true_theta: float, seed: int = None) -> dict:
    """Simulate one adaptive test session for a candidate with known true_theta."""
    rng = random.Random(seed)
    responses = []
    items_used = set()

    for _ in range(MAX_ITEMS + 5):  # allow more tries in case of pool exhaustion
        # Estimate current theta & SEM
        theta_est, sem = estimate_theta_eap(responses)

        # Check stopping
        stop, reason = should_stop(responses, sem)
        if stop:
            break

        # Select item with max Fisher Info at current theta (simplified — no exposure)
        from ai_engine.irt import fisher_information
        candidates = [it for it in ITEMS if it["question_id"] not in items_used]
        if not candidates:
            reason = "pool_exhausted"
            break

        best = max(candidates, key=lambda it: fisher_information(
            theta_est, it["a_param"], it["b_param"], it["c_param"]
        ))
        items_used.add(best["question_id"])

        # Simulate response based on 3PL probability
        p = probability_correct(true_theta, best["a_param"], best["b_param"], best["c_param"])
        is_correct = rng.random() < p

        responses.append({
            "is_correct": is_correct,
            "a_param":    best["a_param"],
            "b_param":    best["b_param"],
            "c_param":    best["c_param"],
        })

    final_theta, final_sem = estimate_theta_eap(responses)
    return {
        "true_theta":   true_theta,
        "est_theta":    final_theta,
        "sem":          final_sem,
        "items":        len(responses),
        "stop_reason":  reason if "reason" in dir() else "unknown",
    }


def run_harness(n_candidates: int = 200, seed: int = 42) -> dict:
    rng = random.Random(seed)
    # Sample true thetas from N(0, 1)
    true_thetas = [rng.gauss(0, 1) for _ in range(n_candidates)]

    results = [simulate_candidate(t, seed=seed + i) for i, t in enumerate(true_thetas)]

    errors   = [r["est_theta"] - r["true_theta"] for r in results]
    bias     = sum(errors) / len(errors)
    rmse     = math.sqrt(sum(e ** 2 for e in errors) / len(errors))
    covered  = sum(
        1 for r in results
        if abs(r["est_theta"] - r["true_theta"]) <= 1.96 * r["sem"]
    )
    coverage = covered / n_candidates * 100
    avg_items = sum(r["items"] for r in results) / n_candidates

    # Reliability: average SEM
    avg_sem = sum(r["sem"] for r in results) / n_candidates
    reliable = avg_sem < SEM_THRESHOLD

    return {
        "n_candidates":        n_candidates,
        "bias":                round(bias,     4),
        "rmse":                round(rmse,     4),
        "sem_coverage_pct":    round(coverage, 2),
        "avg_items_per_test":  round(avg_items, 2),
        "avg_sem":             round(avg_sem,   4),
        "reliability_ok":      reliable,
        "sem_threshold":       SEM_THRESHOLD,
    }


if __name__ == "__main__":
    print("Running evaluation harness …")
    report = run_harness(n_candidates=300)
    print("\n-- Evaluation Report ------------------------------------")
    for k, v in report.items():
        print(f"  {k:25s}: {v}")
    print("---------------------------------------------------")
    if report["reliability_ok"]:
        print("\n+ Scoring reliability within acceptable bounds.")
    else:
        print(f"\n- Average SEM {report['avg_sem']} exceeds threshold {report['sem_threshold']}.")
