from typing import Optional
from pydantic import BaseModel, Json
from datetime import datetime
from .users import User
from .reviewers import Reviewer
from .assessments import Assessment


# assessment tracker used for create: /api/init , update and read
# Shared properties
class Assessment_TrackerBase(BaseModel): # to be modified for functions
    user_id: int
    assessment_id: int
    status: str
    last_updated: datetime
    latest_commit: str
    reviewer_id: Optional[int] = None
    log: Optional[Json] = None

# to create new assessments using user_id/username and assignment ID
# /app/init: https://github.com/Bioinformatics-Research-Network/Skill-cert-API/issues/3
class Assessment_TrackerCreate(Assessment_TrackerBase):
    user_id: int
    assessment_id: int
    status: Optional[str] = None
    last_updated: Optional[datetime] = None
    latest_commit: Optional[str] = None

# used in CRUD utils 
class Assessment_TrackerUpdate(Assessment_TrackerBase):
    status: Optional[str] = None
    last_updated: datetime
    latest_commit: str
    reviewer_id: Optional[int] = None

# update the log for assessments being tracked : app.crud.update_assessment_log
class Assessment_TrackerLogUpdate(Assessment_TrackerBase):
    log: Optional[Json] = None

# additional properties shared by model in DB
class Assessment_TrackerInDBBase(Assessment_TrackerBase):
    entry_id: int
    user_info: User
    assessment_info: Assessment
    reviewer_info: Reviewer

    class Config:
        orm_mode: True

# to read assessment_tracker from DB
class Assessment_Tracker(Assessment_TrackerInDBBase):
    pass
