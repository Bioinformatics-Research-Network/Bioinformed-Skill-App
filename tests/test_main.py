from fastapi.testclient import TestClient
from tests.conftest import *
from fastapi import Depends
from tests.crud.crud import *


def test_random_data(
    client: TestClient,
    db: Session = Depends(override_get_db)
) -> None:
    user = create_random_user(1,db=db)
    reviewer = create_random_reviewers(1,db=db)
    assessment = create_assessments(1, db=db)
    assessment_tracker = create_random_assessment_tracker(1, db=db)
    r = client.get("/")
    assert r.status_code == 400
    assert user
    assert reviewer
    assert assessment
    assert assessment_tracker