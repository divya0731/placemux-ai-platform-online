from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

# Severity levels for proctoring events
EVENT_SEVERITY = {
    "TAB_SWITCH":       "HIGH",
    "WINDOW_DEFOCUS":   "MEDIUM",
    "MULTIPLE_FACES":   "HIGH",
    "NO_FACE":          "HIGH",
    "AUDIO_SPIKE":      "LOW",
    "FULLSCREEN_EXIT":  "HIGH",   # Candidate minimised or exited fullscreen mode
}

class ProctoringLog(Base):
    __tablename__ = "proctoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, index=True)
    event_type = Column(String)
    severity = Column(String, default="MEDIUM")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
