from typing import Optional, List
from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel): # to be modified for functions
    github_username: str
    first_name: str
    last_name: str
    email: EmailStr
    assessments_id: Optional[List[int]] = None # for assessments ongoing or Done


class UserCreate(UserBase):
    github_username: str
    first_name: str
    last_name: str
    email: EmailStr

# request body for updating user information 
# class UserUpdate(UserBase):
#     github_username: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     assessments_id: Optional[List[int]] = None # inputs Assessment_Tracker.entry_id

# Properties shared by models stored in DB useful in `/api/auth`
class UserInDBBase(UserBase):
    user_id: Optional[int] = None
    github_username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode: True

class User(UserInDBBase):
    pass

# additional properties of User in DB
# class UserInDB(UserInDBBase):
#     pass

# can add more custom response model for security
