from typing import Optional, List
from pydantic import BaseModel, Json
from datetime import datetime
from schemas import users, reviewers

# Shared properties
class Assessment_TrackerBase(BaseModel): # to be modified for functions
    user_id: int
    assessment_id: int
    status: str
    last_updated: datetime
    latest_commit: str
    reviewer_id: Optional[int] = None
    log: Optional[Json] = None

# to create new assignments using user_id/username and assignment ID
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

# update the log for assignments being tracked
class Assessment_TrackerLogUpdate(Assessment_TrackerBase):
    log: Optional[Json] = None

# Properties shared by models stored in DB
class Assessment_TrackerInDBBase(Assessment_TrackerBase):
    entry_id: int
    user_id: int
    assessment_id: int
    status: str
    latest_commit: str

    class Config:
        orm_mode: True

# to check for the assignment in process or completed by users in DB, 
class Assessment_Tracker(Assessment_TrackerInDBBase):
    pass

# additional properties stored in DB
# class Assessment_TrackerInDB(Assessment_TrackerInDBBase):
#     pass

# can add more custom response model for security