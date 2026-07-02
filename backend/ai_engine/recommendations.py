"""
ai_engine/recommendations.py — Skills-to-Jobs Matching Engine
==============================================================
Day 6 deliverable: Recommendation v0

Algorithm
---------
1. Build a normalised skills vector from all competency scores.
2. Each role has a requirements vector (competency_id → required proficiency 0–100).
3. Match score = weighted cosine similarity between candidate vector and role vector.
4. Augment with theta (general cognitive ability) contribution.
5. Generate per-role "why this match" explanation referencing actual competency strengths/gaps.

Competency score thresholds:
  Strong ≥ 70  |  Adequate 50–69  |  Gap < 50
"""

import math                                                            
from typing import Optional


# ── Role definitions ─────────────────────────────────────────────────────────
# Each role maps competency_ids to required proficiency (0–100) and carries
# a cognitive_weight that determines how much theta contributes to the score.

ROLE_DATABASE = [
    {
        "role": "AI / ML Engineer",
        "icon": "fa-solid fa-brain",
        "cognitive_weight": 0.45,        # high: abstract reasoning matters a lot
        "requirements": {
            "CSE001": 70,   # Python Advanced
            "CSE002": 65,   # DSA
            "CSE008": 75,   # ML Fundamentals
            "CSE009": 60,   # Deep Learning
            "CSE_ECE002": 55,  # Math
        },
        "explainer_template": (
            "Your demonstrated mastery in {strengths} aligns directly with the core skills "
            "for building and deploying ML pipelines. "
            "{gap_note}"
            "Cognitive ability score (θ={theta:.2f}) further validates readiness for "
            "complex model reasoning tasks."
        ),
    },
    {
        "role": "Backend Software Engineer",
        "icon": "fa-solid fa-server",
        "cognitive_weight": 0.35,
        "requirements": {
            "CSE001": 75,   # Python
            "CSE002": 70,   # DSA
            "CSE006": 65,   # DBMS/SQL
            "CSE007": 55,   # Networks
            "CSE005": 50,   # OS
        },
        "explainer_template": (
            "Strong performance in {strengths} indicates solid foundations for "
            "enterprise-grade backend systems and microservices architecture. "
            "{gap_note}"
        ),
    },
    {
        "role": "Data Analyst / Analytics Engineer",
        "icon": "fa-solid fa-chart-line",
        "cognitive_weight": 0.30,
        "requirements": {
            "CSE001": 60,   # Python
            "CSE002": 55,   # DSA
            "CSE006": 80,   # DBMS/SQL — primary skill
            "CSE_ECE002": 60,  # Math/Stats
        },
        "explainer_template": (
            "Your SQL and data manipulation competencies ({strengths}) make you a strong fit "
            "for analytics pipelines and business intelligence roles. "
            "{gap_note}"
        ),
    },
    {
        "role": "Embedded Systems Engineer",
        "icon": "fa-solid fa-microchip",
        "cognitive_weight": 0.30,
        "requirements": {
            "ECE001": 70,   # Digital Electronics
            "ECE002": 80,   # Embedded C
            "ECE007": 55,   # Control Systems
            "CSE_ECE001": 60,  # Problem Solving
        },
        "explainer_template": (
            "Demonstrated strength in {strengths} underpins the low-level systems and "
            "hardware-software integration skills required for embedded engineering. "
            "{gap_note}"
        ),
    },
    {
        "role": "VLSI / Hardware Design Engineer",
        "icon": "fa-solid fa-memory",
        "cognitive_weight": 0.25,
        "requirements": {
            "ECE001": 80,   # Digital Electronics
            "ECE006": 70,   # VLSI
            "ECE003": 65,   # Analog Electronics
            "ECE004": 55,   # Signals & Systems
        },
        "explainer_template": (
            "Your digital logic and circuit design competencies ({strengths}) map closely "
            "to the skills required for RTL design and chip verification. "
            "{gap_note}"
        ),
    },
    {
        "role": "RF / Communications Engineer",
        "icon": "fa-solid fa-satellite-dish",
        "cognitive_weight": 0.30,
        "requirements": {
            "ECE005": 80,   # Communication Systems — primary
            "ECE004": 70,   # Signals & Systems
            "ECE003": 55,   # Analog Electronics
            "CSE_ECE002": 60,  # Math
        },
        "explainer_template": (
            "Strong signal theory and communications foundation ({strengths}) aligns with "
            "RF engineering, wireless protocol design, and SDR development. "
            "{gap_note}"
        ),
    },
    {
        "role": "Full-Stack Web Developer",
        "icon": "fa-solid fa-globe",
        "cognitive_weight": 0.25,
        "requirements": {
            "CSE001": 65,   # Python
            "CSE010": 75,   # Web Dev — primary
            "CSE006": 55,   # DBMS
            "CSE002": 50,   # DSA
        },
        "explainer_template": (
            "Proficiency in {strengths} supports end-to-end web application development "
            "including frontend interactivity and backend API design. "
            "{gap_note}"
        ),
    },
]

STRONG_THRESHOLD  = 70.0
ADEQUATE_THRESHOLD = 50.0
THETA_RANGE = (-2.5, 2.5)      # theta values outside this range are clipped for scaling


def _scale_theta(theta: float) -> float:
    """Map theta from [THETA_RANGE] to [0, 100]."""
    lo, hi = THETA_RANGE
    return max(0.0, min(100.0, ((theta - lo) / (hi - lo)) * 100.0))


def _cosine_match(candidate_vec: dict, requirements: dict) -> float:
    """
    Weighted cosine-similarity style match.
    Returns a score in [0, 100].
    """
    role_keys = list(requirements.keys())
    if not role_keys:
        return 0.0

    dot = 0.0
    norm_cand = 0.0
    norm_role = 0.0

    for comp_id in role_keys:
        c_score = candidate_vec.get(comp_id, 0.0)   # 0 if competency not tested
        r_score = requirements[comp_id]
        dot      += c_score * r_score
        norm_cand += c_score ** 2
        norm_role += r_score ** 2

    if norm_cand == 0.0 or norm_role == 0.0:
        return 0.0

    cosine = dot / (math.sqrt(norm_cand) * math.sqrt(norm_role))
    return round(cosine * 100.0, 2)


def generate_career_recommendations(
    theta: float,
    competency_scores: dict,
    top_n: Optional[int] = None,
) -> list:
    """
    Generate ranked career recommendations.

    Parameters
    ----------
    theta              : EAP ability estimate from the CAT
    competency_scores  : {competency_id: {"score": float, "skill": str, ...}}
                         (as returned by get_competency_analysis)
    top_n              : If set, returns only the top N matches.

    Returns
    -------
    List of recommendation dicts, sorted by match_percentage descending.
    """
    # ── 1. Build normalised candidate skills vector ───────────────────────────
    # competency_scores values may be dicts (from competency_analysis route)
    # or plain floats. Handle both.
    candidate_vec: dict[str, float] = {}
    for comp_id, value in competency_scores.items():
        if isinstance(value, dict):
            candidate_vec[comp_id] = float(value.get("score", 0.0))
        else:
            candidate_vec[comp_id] = float(value)

    ability_score = _scale_theta(theta)

    recommendations = []

    for role_def in ROLE_DATABASE:
        requirements = role_def["requirements"]
        cog_weight   = role_def["cognitive_weight"]
        skill_weight = 1.0 - cog_weight

        # ── 2. Skill-vector match ─────────────────────────────────────────────
        skill_match = _cosine_match(candidate_vec, requirements)

        # ── 3. Weighted composite score ───────────────────────────────────────
        fit_score = round(
            skill_match * skill_weight + ability_score * cog_weight,
            1
        )
        fit_score = max(25.0, min(99.0, fit_score))

        # ── 4. Identify strengths and gaps ────────────────────────────────────
        strengths: list[str] = []
        gaps: list[str]      = []
        for comp_id, req_level in requirements.items():
            cand_level = candidate_vec.get(comp_id, 0.0)
            skill_name = competency_scores.get(comp_id, {})
            if isinstance(skill_name, dict):
                skill_name = skill_name.get("skill", comp_id)
            else:
                skill_name = comp_id

            if cand_level >= STRONG_THRESHOLD:
                strengths.append(skill_name)
            elif cand_level < ADEQUATE_THRESHOLD and req_level >= 65:
                gaps.append(skill_name)

        # If no tested competencies overlap with role, flag that
        tested_overlap = [k for k in requirements if k in candidate_vec]

        # ── 5. Generate explanation ───────────────────────────────────────────
        strengths_str = ", ".join(strengths) if strengths else "general cognitive ability"
        gap_note = (
            f"Areas to develop: {', '.join(gaps[:2])}. "
            if gaps else ""
        )
        if not tested_overlap:
            gap_note = "Note: these competencies were not assessed in this session. Score is θ-based. "

        template = role_def["explainer_template"]
        explainer = template.format(
            strengths=strengths_str,
            gap_note=gap_note,
            theta=theta,
        )

        recommendations.append({
            "role":             role_def["role"],
            "icon":             role_def["icon"],
            "match_percentage": fit_score,
            "required_skills":  list(requirements.keys()),
            "candidate_strengths": strengths,
            "candidate_gaps":   gaps,
            "explainer":        explainer,
        })

    # ── 6. Sort and return ────────────────────────────────────────────────────
    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
    if top_n is not None:
        recommendations = recommendations[:top_n]

    return recommendations
