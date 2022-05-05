from pydantic import BaseModel


class user_check(BaseModel):
    """
    Pydantic request model schema used by `/api/init_assessment` endpoint
    """
    github_username: str


# make schemas assessment_tracker_init for `/api/init_assessment`
# to create new assessment_tracker entry
# takes in assessment info
class assessment_tracker_init(BaseModel):
    """
    Pydantic request model schema used by `/api/init_assessment` endpoint
    """
    assessment_name: str
    latest_commit: str


class approve_assessment(BaseModel):
    """
    Pydantic request model schema used by `/api/approve_assessment` endpoint
    """
    reviewer_username: str
    member_username: str  # username of the member whose assessment is to be approved
    assessment_name: str


class check_update(BaseModel):
    """
    Pydantic request model schema used by `/api/init_check` and `/api/update` endpoint
    """
    github_username: str
    assessment_name: str
    commit: str

    class Config:
        orm_mode = True

    # other info required by GHA can be entered here


# logs schemas is used so as logs are not enterd as parameter rather as request body
class update_log(BaseModel):
    """
    Pydantic request model schema used by `/api/update` endpoint
    """
    log: dict

    class Config:
        orm_mode = True


class response_init_assessment(BaseModel):
    """
    Pydantic response model schema used by `/api/init_assessment` endpoint
    """
    Initiated: bool
    User_first_name: str
