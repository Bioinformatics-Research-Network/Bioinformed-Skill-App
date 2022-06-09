# from app.db import db_session
# from app.models import Users, Assessments, Reviewers, Badges, Assertions
# from app import utils, crud
# from app.config import settings

from sync import sync
from sync.config import settings


# def test_crud_user(client):
#     """
#     Test that users can be created and deleted
#     """
#     try:
#         # Try to create a user. It will fail if they already exist.
#         db_session.add(Users(username="test_user", name="test_user"))
#         db_session.commit()
#     except: 
#         # If the user already exists, delete it.
#         db_session.rollback()

#     # Check that the user was created
#     user = db_session.query(Users).filter_by(username="test_user").first()
#     assert user.username == "test_user"

#     # Drop User table
#     db_session.query(Users).delete()
#     db_session.commit()

#     # Check that the user was dropped
#     user = db_session.query(Users).filter_by(username="test_user").first()
#     assert user is None


# def test_sync_badges(client):
#     """
#     Test that badges can be synced
#     """
#     utils.sync_badges(settings)


# def test_sync_assertions(client):
#     """
#     Test that assertions can be synced
#     """
#     utils.sync_assertions(settings)


# def test_get_assertions_by_user():
#     """
#     Test that assertions can be retrieved by user
#     """
#     # Create a user
#     user = db_session.query(Users).filter_by(username="test_user").first()
#     assertions = crud.get_assertions_by_user(
#         db=db_session, user=user
#     )
#     assert assertions is not None


def test_sync_assessments():
    """
    Test that assessments can be synced
    """

    # # Drop all assessments
    # db_session.query(Assessments).delete()
    # db_session.commit()

    # Sync assessments
    assert sync.sync_assessments()

    # # Sync again (update)
    # assert utils.sync_assessments()


def test_sync_releases():
    """
    Test that releases can be synced
    """
    # Sync releases
    sync.download_releases_from_github(settings=settings)

    # Update releases to AWS
    sync.upload_releases_to_aws(settings=settings)
