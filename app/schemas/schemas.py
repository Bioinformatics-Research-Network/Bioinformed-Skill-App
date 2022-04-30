# writing the schemas needed
# these will be devided into different files when needed

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Json, validator

# make schemas user_check for `/api/init_assessment' endpoint
# take in gitusername
class user_check(BaseModel):
    # email: Optional[EmailStr] = None email can be used to check user
    github_username: str


# make schemas assessment_tracker_init for `/api/init_assessment`
# to create new assessment_tracker entry
# takes in assessment info
class assessment_tracker_init(BaseModel):
    assessment_name: str
    latest_commit: str


class approve_assessment(BaseModel):
    reviewer_username: str
    member_username: str  # username of the member whose assessment is to be approved
    assessment_name: str


class check_update(BaseModel):
    github_username: str
    assessment_name: str
    commit: str

    class Config:
        orm_mode = True

    # other info required by GHA can be entered here


# logs schemas is used so as logs are not enterd as parameter rather as request body
class update_log(BaseModel):
    log: Json

    class Config:
        orm_mode = True


class response_init_assessment(BaseModel):
    Initiated: bool
    User_first_name: str
