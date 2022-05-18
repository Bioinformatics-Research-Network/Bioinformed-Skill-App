# Script for issue badge to a user
import requests
import json


def get_bearer_token(config: dict):
    """
    Get the bearer token from the Badgr API.
    Scope is limited to read-only access for organization-level badges.
    Includes write access for user-level badges.

    :param config: The configuration dictionary for the Badgr API

    :return: The bearer token as a string
    """
    url = config["BADGR_BASE_URL"] + "/o/token/"
    payload = {
        "username": config["BADGR_USERNAME"],
        "password": config["BADGR_PASSWORD"],
        "scope": config["BADGR_SCOPE"],
        "grant_type": config["BADGR_GRANT_TYPE"],
        "client_id": config["BADGR_CLIENT_ID"],
    }
    response = requests.request("POST", url, data=payload)
    return response.json()["access_token"]


def get_assertion(
    assessment_name: str, user_email: str, bearer_token: str, config: dict
):
    """
    Get the badge assertion from the Badgr API

    :param assessment_name: The assessment name
    :param user_email: The user's email
    :param bearer_token: The bearer token (from the Badgr API)
    :param config: The configuration dictionary for the Badgr API

    :return: The assertion as a response object
    """
    url = (
        config["BADGR_BASE_URL"]
        + "/v2/badgeclasses/"
        + config["BADGE_IDs"][assessment_name]
        + "/assertions"
        + "?recipient="
        + user_email
        + "&num=1"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }

    response = requests.request("GET", url, headers=headers)
    return response


def get_all_assertions(
    assessment_name: str,
    bearer_token: str,
    config: dict,
):
    """
    Get all assertions for a user

    :param user_email: The user's email
    :param user_first: The user's first name
    :param user_last: The user's last name
    :param assessment_name: The assessment name
    :param bearer_token: The bearer token (from the Badgr API)
    :param config: The configuration dictionary for the Badgr API

    :return: The assertion as a response object
    """
    # Get the URL for the badge, based on assessment name
    url = (
        config["BADGR_BASE_URL"]
        + "/v2/badgeclasses/"
        + config["BADGE_IDs"][assessment_name]
        + "/assertions"
    )

    # Prepare the payload with custom text and evidence
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }
    response = requests.request("GET", url, headers=headers)
    return response


# TODO: Pydantic schema for this?
def issue_badge(
    user_email: str,
    user_first: str,
    user_last: str,
    assessment_name: str,
    bearer_token: str,
    config: dict,
):
    """
    Issue a badgr badge to a user

    :param user_email: The user's email
    :param user_first: The user's first name
    :param user_last: The user's last name
    :param assessment_name: The assessment name
    :param bearer_token: The bearer token (from the Badgr API)
    :param config: The configuration dictionary for the Badgr API

    :return: The assertion as a response object
    """
    # Get the URL for the badge, based on assessment name
    url = (
        config["BADGR_BASE_URL"]
        + "/v2/badgeclasses/"
        + config["BADGE_IDs"][assessment_name]
        + "/assertions"
    )

    # Prepare the payload with custom text and evidence
    payload = json.dumps(
        {
            "recipient": {"identity": user_email, "type": "email", "hashed": True},
            "narrative": "This award certifies that "
            + user_first
            + " "
            + user_last
            + " has successfully completed the Bioinformatics Research Network "
            + assessment_name
            + " skill assessment.",
            "evidence": [
                {"narrative": "Link to a place where someone can see the results???"}
            ],
            "notify": True,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response
