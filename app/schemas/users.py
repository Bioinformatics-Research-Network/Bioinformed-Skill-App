from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .assessment_tracker import Assessment_Tracker

# User table is read only: https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#
# Shared properties
class UserBase(BaseModel):
    github_username: str
    first_name: str
    last_name: str
    email: EmailStr


# additional properties of models stored in DB other than UserBase
class UserInDBBase(UserBase):
    user_id: int
    assessments_submitted: Optional(List[Assessment_Tracker]) = None

    class Config:
        orm_mode: True


# read user data from database
class User(UserInDBBase):
    pass
