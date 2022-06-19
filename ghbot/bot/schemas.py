from re import S
from pydantic import BaseModel


# Create init schema
class InitBotRequest(BaseModel):
    """
    Schema for the init command
    """

    name: str
    install_id: int
    repo_prefix: str
    github_org: str
    username: str
    template_repo: str
    latest_release: str
    review_required: bool


class DeleteBotRequest(BaseModel):
    """
    Schema for the delete command
    """

    name: str
    install_id: int
    repo_name: str
    github_org: str
    username: str
