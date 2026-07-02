from sqlalchemy import Column, Integer, String
from database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id     = Column(Integer, primary_key=True, index=True)
    name   = Column(String)
    email  = Column(String, unique=True, index=True)
    branch = Column(String, nullable=True)   # CSE | ECE | EEE | IT | MECH | …
    college = Column(String, nullable=True)  # Institution name (used in fairness grouping)
    year_of_study = Column(String, nullable=True)  # e.g. "3rd Year", "Final Year"