from typing import Optional
from pydantic import BaseModel
from .users import User
from .assessment_tracker import Assessment_Tracker

# Reviewers is Update and read: https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#
# Shared properties
class ReviewerBase(BaseModel): # to be modified for functions
    user_id: int
    assessment_reviewing_id: Optional[int] = None


# to assign assessments to reviewers
class ReviewerUpdate(ReviewerBase):
    assessment_reviewing_id: int

# additional properties shared by reviewers stored in DB
class ReviewerInDBBase(ReviewerBase):
    reviewer_id: int
    user_info: User
    assessment_reviewing_info: Optional[Assessment_Tracker] = None

    class Config:
        orm_mode: True

# get reviewer data from DB.
class Reviewer(ReviewerInDBBase):
    pass
