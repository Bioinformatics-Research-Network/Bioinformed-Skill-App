from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr, Json
from app.schemas import assessmenttracker
from schemas import users

# Shared properties
class ReviewerBase(BaseModel): # to be modified for functions
    user_id: int
    assessments_reviewing_id: Optional[int] = None

# create new reviewers, helps in creating fake data
class ReviewerCreate(ReviewerBase):
    user_id: int

# to assign assignments to reviewers
class ReviewerUpdate(ReviewerBase):
    assessments_reviewing_id: int

# Properties shared by models stored in DB
class ReviewerInDBBase(ReviewerBase):
    reviewer_id: Optional[int] = None
    user_id: Optional[int] = None
    assessments_reviewing_id: Optional[int] = None

    class Config:
        orm_mode: True

# to check if the user is a reviewer
class Reviewer(ReviewerInDBBase):
    pass

# additional properties stored in DB
# class ReviewerInDB(ReviewerInDBBase):
#     pass

# can add more custom response model for security