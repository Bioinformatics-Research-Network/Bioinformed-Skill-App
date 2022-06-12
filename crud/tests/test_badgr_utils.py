from app.utils import badgr_utils
from app.dependencies import get_settings
from fastapi.testclient import TestClient


def test_issue_badge(
    client: TestClient,
):
    """
    Test the issue_badge function
    """

    # Get the config from the testclient object
    config = client.app.dependency_overrides[get_settings]()

    # Get the bearer token
    brearer_token = badgr_utils.get_bearer_token(config)

    # Issue the badge
    issue_badge_response = badgr_utils.issue_badge(
        user_email="tests@bioresnet.org",
        user_first="Test",
        user_last="User",
        assessment_name="Test",
        bearer_token=brearer_token,
        config=config,
    )

    # Wrangle the response
    recip = issue_badge_response.json()["result"][0]["recipient"]

    # Assert that the badge was issued correctly
    assert issue_badge_response.status_code == 201
    assert issue_badge_response.json()["status"]["success"]
    assert recip["plaintextIdentity"] == "tests@bioresnet.org"


def test_get_assertion(
    client: TestClient,
):
    """
    Test the get_badge_json function
    """

    # Get the config from the testclient object
    config = client.app.dependency_overrides[get_settings]()

    # Get the bearer token
    brearer_token = badgr_utils.get_bearer_token(config)

    # Get the badge JSON
    badge_assertion = badgr_utils.get_assertion(
        assessment_name="Test",
        user_email="tests@bioresnet.org",
        bearer_token=brearer_token,
        config=config,
    )

    # Wrangle the badge JSON
    result = badge_assertion.json()["result"]
    recip = result[0]["recipient"]["plaintextIdentity"]
    assessment_name = result[0]["badgeclass"]

    # Assert that the badge JSON is correct
    assert badge_assertion.status_code == 200
    assert badge_assertion.json()["status"]["success"]
    assert recip == "tests@bioresnet.org"
    assert assessment_name == config.BADGE_IDs["Test"]
