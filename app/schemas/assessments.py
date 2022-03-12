from typing import Optional, List
from pydantic import BaseModel, Json
from schemas import assessments

class Assessments(BaseModel):
    id: int
    name: str
    version_number: Optional[str] = None
    change_log: Optional[Json] = None
    description: Optional[str] = None
    pre_requisites_id: Optional[int] = None
    pre_requisites: Optional[List[assessments.Assessments]] = None
    goals: Optional[str]

    class Config:
        orm_mode = True

