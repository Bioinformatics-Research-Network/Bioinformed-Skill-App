from pydantic import BaseModel


## Request schemas


class InitRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/init` endpoint
    """

    github_username: str
    assessment_name: str
    latest_commit: str


class CheckRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/check` endpoint
    """

    github_username: str
    assessment_name: str
    latest_commit: str

    class Config:
        orm_mode = True


class ApproveRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/approve` endpoint
    """

    latest_commit: str
    reviewer_username: str


class UpdateRequest(BaseModel):
    """
    Pydantic request model schema used by the `/api/update` endpoint
    """

    github_username: str
    assessment_name: str
    commit: str
    log: dict

    class Config:
        orm_mode = True


class ReviewRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/review` endpoint
    """

    commit: str

    class Config:
        orm_mode = True


## Response schemas


class InitResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/init` endpoint
    """

    Initiated: bool
    User_first_name: str
