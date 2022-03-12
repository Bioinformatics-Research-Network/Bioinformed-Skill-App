from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr, Json
from datetime import datetime

class Users(BaseModel):
    id: int
    github_username: str
    first_name: str
    last_name: str
    email: EmailStr
    assessments_id: int
    assessments: List[Assessments] = []

    class Config:
        orm_mode = True


class Reviewers(BaseModel):
    id: str
    user_id: int
    assessments_reviewing: Optional[List[Assessment_Tracker]] = None

    class Config:
        orm_mode = True



class Assessment_Tracker(BaseModel):
    entry_id: int
    user_id: int
    user: Users
    assessment_id: int
    status: str
    last_updated: datetime
    latest_commit: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewers: Optional[List[Reviewers]] = None
    log: Optional[Json] = None

    class Config:
        orm_mode = True



class Assessments(BaseModel):
    id: int
    name: str
    version_number: Optional[str] = None
    change_log: Optional[Json] = None
    description: str
    pre_requisites_id: Optional[int] = None
    pre_requisites: Optional[Assessments] = None
    goals: Optional[str]

    class Config:
        orm_mode = True

