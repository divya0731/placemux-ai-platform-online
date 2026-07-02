from pydantic import BaseModel
from typing import Optional, List

class CandidateCreate(BaseModel):
    name: str
    email: str
    branch: Optional[str] = None
    college: Optional[str] = None
    year_of_study: Optional[str] = None

class NextQuestionRequest(BaseModel):
    candidate_id: int
    current_difficulty: str
    last_response_correct: Optional[bool] = None

class NextQuestionResponse(BaseModel):
    next_question_id: Optional[str]
    question_text: Optional[str]
    difficulty: str
    options: Optional[List[str]] = None
    competency_id: Optional[str] = None
    cluster_id: Optional[str] = None
    bloom_level: Optional[str] = None
    item_type: Optional[str] = None
    finished: bool = False
    stop_reason: Optional[str] = None
    current_theta: Optional[float] = None
    current_sem: Optional[float] = None
    items_answered: int = 0
    parameter_source: str = "seeded"  # "seeded" | "empirical"

class SubmitAnswerRequest(BaseModel):
    candidate_id: int
    question_id: str
    selected_option: str
    response_time_ms: Optional[int] = None  # client-side timing

class ProctoringEventRequest(BaseModel):
    candidate_id: int
    event_type: str

class ProctoringVerdictResponse(BaseModel):
    risk_score: int
    verdict: str
    violations_count: int
    is_disqualified: bool = False

class FinalScoreResponse(BaseModel):
    ability_estimate: float
    sem: float
    scaled_score: float
    percentile: Optional[float] = None  # percentile rank among all scored candidates

class FinalScoreRequest(BaseModel):
    candidate_id: int

class SkillMatchDetail(BaseModel):
    competency_id: str
    skill_name: str
    score: float
    weight: float

class RecommendationResponse(BaseModel):
    role: str
    icon: str
    match_percentage: float
    required_skills: List[str]
    candidate_strengths: List[str]   # competencies that boosted this match
    candidate_gaps: List[str]        # competencies below the role's threshold
    explainer: str
