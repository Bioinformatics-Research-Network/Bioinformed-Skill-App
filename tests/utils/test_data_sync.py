from app.db import db_session
from app.models import Users


def test_index(client):
    """
    Test that index page is accessible without login
    """
    response = client.get("/")
    assert response.status_code == 200


def test_crud_user(client):
    """
    Test that users can be created and deleted
    """
    try:
        # Try to create a user. It will fail if they already exist.
        db_session.add(Users(username="test_user", name="test_user"))
        db_session.commit()
    except: 
        # If the user already exists, delete it.
        db_session.rollback()

    # Check that the user was created
    user = db_session.query(Users).filter_by(username="test_user").first()
    assert user.username == "test_user"

    # Drop User table
    db_session.query(Users).delete()
    db_session.commit()

    # Check that the user was dropped
    user = db_session.query(Users).filter_by(username="test_user").first()
    assert user is None



