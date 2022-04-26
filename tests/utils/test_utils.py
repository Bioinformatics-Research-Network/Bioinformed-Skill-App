from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import Json
from sqlalchemy.orm import Session
from app.schemas import schemas

# app.utils.runGHA 
def test_runGHA(
    client: TestClient,
    db: Session,
    check: schemas.check_update
    ):