"""
Fairness Check — ai_engine/fairness_check.py
=============================================
Day 7 deliverable: Fairness sanity check across sub-groups.

Compares score distributions across different engineering branches (CSE / ECE)
for obvious disparate impact and logs flags for Phase 2 review.

Usage (offline):
    python ai_engine/fairness_check.py

Usage (from API):
    from ai_engine.fairness_check import run_fairness_check
    report = run_fairness_check(candidate_scores_by_group)
"""

import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Statistics helpers ───────────────────────────────────────────────────────

def mean(values):
    return sum(values) / len(values) if values else 0.0

def std_dev(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

def cohen_d(group_a, group_b):
    """Effect size: standardised mean difference between two groups."""
    if len(group_a) < 2 or len(group_b) < 2:
        return 0.0
    pooled_sd = math.sqrt((std_dev(group_a) ** 2 + std_dev(group_b) ** 2) / 2)
    if pooled_sd == 0:
        return 0.0
    return (mean(group_a) - mean(group_b)) / pooled_sd

def four_fifths_ratio(mean_a, mean_b):
    """
    EEOC 4/5ths (80%) rule: if the selection rate of the lower-scoring group
    is below 80 % of the higher-scoring group, the test may have adverse impact.
    We use mean scaled scores as a proxy for selection rates here.
    """
    if mean_a == 0 or mean_b == 0:
        return None
    ratio = min(mean_a, mean_b) / max(mean_a, mean_b)
    return round(ratio, 3)


# ── Core fairness analysis ────────────────────────────────────────────────────

def run_fairness_check(scores_by_group: dict) -> dict:
    """
    scores_by_group: {group_name: [scaled_score, ...]}
      e.g. {"CSE": [78, 82, 55, ...], "ECE": [60, 70, 48, ...]}

    Returns a structured fairness report.
    """
    report = {}
    group_stats = {}

    for group, scores in scores_by_group.items():
        if not scores:
            continue
        group_stats[group] = {
            "n":       len(scores),
            "mean":    round(mean(scores), 2),
            "std_dev": round(std_dev(scores), 2),
            "min":     round(min(scores), 2),
            "max":     round(max(scores), 2),
        }

    report["group_statistics"] = group_stats

    # Pairwise comparisons
    groups = list(group_stats.keys())
    comparisons = []
    flags = []

    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            ga, gb = groups[i], groups[j]
            d = cohen_d(scores_by_group[ga], scores_by_group[gb])
            ratio = four_fifths_ratio(
                group_stats[ga]["mean"], group_stats[gb]["mean"]
            )

            flag_raised = False
            flag_msgs = []

            # Flag if Cohen's d > 0.5 (medium+ effect size)
            if abs(d) > 0.5:
                flag_raised = True
                flag_msgs.append(
                    f"Large effect size (d={round(d,3)}) — may indicate systematic bias."
                )

            # Flag if 4/5ths ratio < 0.80
            if ratio is not None and ratio < 0.80:
                flag_raised = True
                flag_msgs.append(
                    f"4/5ths ratio = {ratio} < 0.80 — potential adverse impact."
                )

            comp = {
                "groups":           f"{ga} vs {gb}",
                "cohen_d":          round(d, 3),
                "four_fifths_ratio": ratio,
                "flagged":          flag_raised,
                "flags":            flag_msgs,
            }
            comparisons.append(comp)
            if flag_raised:
                flags.extend(flag_msgs)

    report["pairwise_comparisons"] = comparisons
    report["total_flags"] = len(flags)
    report["flag_summary"] = flags
    report["action"] = (
        "PHASE-2 REVIEW REQUIRED — Disparate impact detected." if flags
        else "No significant disparate impact found. Continue to Phase 2 monitoring."
    )

    return report


# ── Demo / CLI ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import random
    rng = random.Random(99)

    # Simulate two groups with a slight mean gap
    demo_scores = {
        "CSE": [min(100, max(0, rng.gauss(72, 15))) for _ in range(80)],
        "ECE": [min(100, max(0, rng.gauss(65, 18))) for _ in range(60)],
    }

    report = run_fairness_check(demo_scores)

    print("\n-- Group Statistics ------------------------------------------")
    for g, stats in report["group_statistics"].items():
        print(f"  {g}: n={stats['n']}, mean={stats['mean']}, sigma={stats['std_dev']}")

    print("\n-- Pairwise Comparisons --------------------------------------")
    for c in report["pairwise_comparisons"]:
        print(f"  {c['groups']}: d={c['cohen_d']}, 4/5ths={c['four_fifths_ratio']}, "
              f"flagged={c['flagged']}")
        for f in c["flags"]:
            print(f"    [FLAG] {f}")

    print(f"\n  Total flags : {report['total_flags']}")
    print(f"  Action      : {report['action']}")
