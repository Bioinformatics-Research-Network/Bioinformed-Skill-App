from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr, Json
from schemas import users, assessment_tracker


class Reviewers(BaseModel):
    id: str
    user_id: int
    user: users.User
    assessments_reviewing: Optional[List[assessment_tracker.Assessment_Tracker]] = None

    class Config:
        orm_mode = True

