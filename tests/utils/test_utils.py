from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import Json
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.utils.utils import runGHA

# app.utils.runGHA 
def test_runGHA(
    client: TestClient
    ):
    request_json = schemas.check_update(
        github_username =  "test",
        assessment_name = "test",
        commit = "test",
    )
    log = runGHA(check=request_json) # logs = {"Updated": str(datetime.utcnow()), "Checks_passed": True, "Commit": commit}

    assert type(log["Updated"]) == str
    assert log["Checks_passed"] == True
    assert type(log["Commit"]) == str