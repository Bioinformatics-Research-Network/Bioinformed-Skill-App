from typing import Optional
from pydantic import BaseModel
from datetime import datetime


# Request schemas


class InitRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/init` endpoint
    """

    user_id: int
    assessment_id: int


class CheckRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/check` endpoint
    """

    latest_commit: str
    passed: bool


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

    username: str
    assessment_name: str


class DeleteAssessmentTrackerRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/delete` endpoint
    """

    user_id: str
    assessment_id: str


class DeleteUserRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/delete` endpoint
    """

    user_id: str


class UpdateRequest(BaseModel):
    """
    Pydantic request model schema used by the `/api/update` endpoint
    """

    username: str
    assessment_name: str
    latest_commit: str
    log: dict
    status: Optional[str] = None


class ReviewRequest(BaseModel):
    """
    Pydantic request model schema used by `/api/review` endpoint
    """

    latest_commit: str


class AddReviewerRequest(BaseModel):
    """
    Pydantic response model schema used by `/api/add_reviewer` endpoint
    """

    reviewer_username: str
    slack_id: int


# Response schemas

# no such api end point
# class RegisterResponse(BaseModel):
#     """
#     Pydantic response model schema used by `/api/register` endpoint
#     """

#     registered: bool


class InitResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/init` endpoint
    """

    Initiated: bool


class ReviewResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/review` endpoint
    """

    reviewer_id: int
    reviewer_username: str


class CheckResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/check` endpoint
    """

    Check: bool
    review_required: int


class ApproveResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/approve` endpoint
    """

    Assessment_Approved: bool


class UpdateResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/update` endpoint
    """

    Logs_updated: bool


class DeleteResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/delete` endpoint
    """

    Entry_deleted: bool


class DeleteUserResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/delete_user` endpoint
    """

    User_deleted: bool


class ViewResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/view` endpoint
    """

    id: int
    user_id: int
    assessment_id: int
    status: str
    last_updated: datetime
    latest_commit: str


class AddReviewerResponse(BaseModel):
    """
    Pydantic response model schema used by `/api/add_reviewer` endpoint
    """

    Reviewer_added: bool
