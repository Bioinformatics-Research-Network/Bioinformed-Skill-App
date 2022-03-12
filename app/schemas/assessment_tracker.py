from typing import Optional, List
from pydantic import BaseModel, Json
from datetime import datetime
from schemas import users, reviewers

class Assessment_Tracker(BaseModel):
    entry_id: int
    user_id: int
    user: users.User
    assessment_id: int
    status: str
    last_updated: datetime
    latest_commit: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewers: Optional[List[reviewers.Reviewers]] = None
    log: Optional[Json] = None

    class Config:
        orm_mode = True
