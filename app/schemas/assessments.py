from typing import Optional, List
from pydantic import BaseModel, Json


class Assessments(BaseModel): # to be modified for functions
    id: int
    name: str
    version_number: Optional[str] = None
    change_log: Optional[Json] = None
    description: Optional[str] = None
    pre_requisites_id: Optional[int] = None
    pre_requisites: Optional[List['Assessments']] = None # self referencing models
    goals: Optional[str]

    class Config:
        orm_mode = True

