from sqlalchemy import Column, Integer, Float
from database import Base

class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, unique=True, index=True)
    ability_estimate = Column(Float)
    sem = Column(Float)
    scaled_score = Column(Float)
