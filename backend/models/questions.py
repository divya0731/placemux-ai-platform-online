from sqlalchemy import Column, Integer, String, Float
from database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # ── Identity ──────────────────────────────────────────────────────────────
    question_id   = Column(String, unique=True, index=True)
    competency_id = Column(String, index=True)   # e.g. "CSE001"
    sub_competency = Column(String, nullable=True)  # granular skill tag, e.g. "OOP Principles"
    cluster_id    = Column(String, index=True, nullable=True)  # e.g. "Programming"

    # ── Classification ────────────────────────────────────────────────────────
    difficulty    = Column(String)               # "Easy" | "Medium" | "Hard"
    bloom_level   = Column(String, nullable=True)  # Remember | Understand | Apply | Analyze | Evaluate | Create
    item_type     = Column(String, default="MCQ")  # MCQ | multi-select | coding | numeric

    # ── Content ───────────────────────────────────────────────────────────────
    question      = Column(String)
    option_a      = Column(String)
    option_b      = Column(String)
    option_c      = Column(String)
    option_d      = Column(String)
    correct_answer = Column(String)
    distractor_rationale = Column(String, nullable=True)  # SME notes on wrong options

    # ── 3PL IRT Parameters ────────────────────────────────────────────────────
    a_param       = Column(Float, default=1.0)   # Discrimination
    b_param       = Column(Float, default=0.0)   # Difficulty
    c_param       = Column(Float, default=0.25)  # Guessing probability

    # ── Exposure Control ──────────────────────────────────────────────────────
    exposure_cap  = Column(Integer, default=50)  # Max times item may be administered
    exposure_count = Column(Integer, default=0)  # Running counter (updated by CAT)