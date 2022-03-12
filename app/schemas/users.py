from typing import Optional, List
from pydantic import BaseModel, validator, EmailStr, Json
from schemas import assessments

class Users(BaseModel): # to be modified for functions
    id: int
    github_username: str
    first_name: str
    last_name: str
    email: EmailStr
    assessments_id: Optional[int] = None
    assessments: Optional[List[assessments.Assessments]] = None

    class Config:
        orm_mode = True