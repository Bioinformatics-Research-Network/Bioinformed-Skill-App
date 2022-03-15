from typing import Optional, List
from pydantic import BaseModel, Json
from sqlalchemy import true

# Shared properties
class AssessmentBase(BaseModel): 
    name: str
    version_number: Optional[str] = None
    change_log: Optional[Json] = None
    description: Optional[str] = None
    pre_requisites_id: Optional[List[int]] = None
    goals: Optional[str]


# create new training requirements,  used in creating fake data
class AssessmentCreate(AssessmentBase):
    name: str
    version_number: Optional[str] = "1"
    description: str
    pre_reqisites_id: List[int]
    goals: str

# to maintain and update training requirements
class AssessmentUpdate(AssessmentBase):
    version_number: Optional[str] = "1"
    description: Optional[str] = None
    pre_reqisites_id: Optional[List[int]] = None
    goals: Optional[str]

# update Log after each update
class AssessmentLogUpdate(AssessmentBase):
    change_log: Optional[Json] = None

# Properties shared by models stored in DB
class AssessmentInDBBase(AssessmentBase):
    assessment_id: int
    name: str

    class Config:
        orm_mode: True

# finding assignment in the DB
class Assessment(AssessmentInDBBase):
    pass

# additional properties stored in DB
# class AssessmentInDB(AssessmentInDBBase):
#     pass

# can add more custom response model for security
