# starting with tests for api endpoints
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import Json
from sqlalchemy.orm import Session
from app.schemas import schemas

# /api/init-assessment
def test_init_assessment(*,
    client: TestClient,
    db: Session,
    user: schemas.user_check,
    assessment_tracker: schemas.assessment_tracker_init
    ):
    

# /api/init-check
def test_init_check(*,
    client: TestClient,
    db: Session,
    asses_track_info: schemas.check_update
    ):

# /api/update
def test_update(*,
    client: TestClient,
    db: Session,
    asses_track_info: schemas.check_update,
    update_logs: Json
    ):

# /api/approve-assessment
def test_approve_assessment(*,
    client: TestClient,
    db: Session,
    approve_assessment: schemas.approve_assessment
    ):

# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer