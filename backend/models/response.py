from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

class Response(Base):
    __tablename__ = "responses"

    id              = Column(Integer, primary_key=True, index=True)
    candidate_id    = Column(Integer, index=True)
    question_id     = Column(String, index=True)
    selected_option = Column(String)
    is_correct      = Column(Boolean)
    difficulty      = Column(String)
    competency_id   = Column(String, nullable=True)  # denormalised for fast per-competency queries
    response_time_ms = Column(Integer, nullable=True) # how long the candidate took (ms)
