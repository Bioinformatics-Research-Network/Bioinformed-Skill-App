from typing import List
from pydantic import BaseModel, Json

# Assessments are read only: https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#
# Shared properties
class AssessmentBase(BaseModel):
    name: str
    version_number: str
    change_log: Json
    description: str
    pre_requisites_ids: List[int]
    goals: str


# update Log, not mentioned in workflow, but left undeleted for timebeing
# class AssessmentLogUpdate(AssessmentBase):
#     change_log: Optional[Json] = None


# Properties shared by models stored in DB
class AssessmentInDBBase(AssessmentBase):
    assessment_id: int
    pre_requisites_info: List["Assessment"]

    class Config:
        orm_mode: True


# finding assignment in the DB
class Assessment(AssessmentInDBBase):
    pass
