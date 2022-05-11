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

    latest_commit: str


class ApproveRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/approve` endpoint
    """

    latest_commit: str
    reviewer_username: str


class ViewRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/view` endpoint
    """

    github_username: str
    assessment_name: str


class DeleteRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/delete` endpoint
    """

    github_username: str
    assessment_name: str


class UpdateRequest(BaseModel):
    """
    Pydantic request model schema used by the `/api/update` endpoint
    """

    github_username: str
    assessment_name: str
    latest_commit: str
    log: dict


class ReviewRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/review` endpoint
    """

    latest_commit: str


## Response schemas


class InitResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/init` endpoint
    """

    Initiated: bool
    User_first_name: str


class ReviewResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/review` endpoint
    """

    reviewer_id: int
    reviewer_username: str
