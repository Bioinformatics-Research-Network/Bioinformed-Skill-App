from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .assessment_tracker import Assessment_Tracker

# User table is read only
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

