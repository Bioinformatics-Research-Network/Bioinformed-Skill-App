import json
from app import crud
from sqlalchemy.orm import Session
import copy
import requests
from datetime import datetime
from app.dependencies import Settings
import app.db.models as models


def ask_reviewer(
    db: Session,
    assessment_tracker_entry: models.AssessmentTracker,
    reviewer_info: dict,
    settings: Settings,
):
    """
    Send a message to the reviewer asking them to review the trainee's assessment.

    :param db: Database session
    :param assessment_tracker_entry: AssessmentTracker entry
    :param reviewer_info: Dictionary containing reviewer info
    :param settings: Settings object
    :return: response object
    """
    user = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)

    reviewer_slack = crud.get_user_by_username(
        db=db, username=reviewer_info.reviewer_username
    )

    assessment = crud.get_assessment_by_id(
        db=db, assessment_id=assessment_tracker_entry.assessment_id
    )
    filename = "app/slack_utils/review_request.json"
    with open(filename, "r") as f:
        data = json.load(f)
        payload = copy.deepcopy(data)
        payload["blocks"][0]["text"][
            "text"
        ] = f"Please confirm if you would like to review the assessment for:\nTrainee Name: {user.name}\nAssessment: {assessment.name}"
        payload["blocks"][1]["text"]["text"] = f"<@{str(reviewer_slack.slack_id)}>"
        # payload['blocks'][1]['text']['text']=(f"<@{test1_slack_id}>\n")

        response = requests.post(url=settings.SLACK_BOT_URL, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e: 
            raise e
        except Exception as e:
            raise e
    return response


def confirm_reviewer(
    db: Session,
    slack_payload: dict,
    settings: Settings,
):
    """
    Confirms that the reviewer has agreed to review the trainee's assessment.

    :param db: Database session
    :param assessment_name: Assessment name
    :param response_url: Slack response URL
    :param trainee_name: Trainee name
    :param reviewer_slack_id: Slack ID of the reviewer
    :return: response object
    """

    # user = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)
    # user_name = user.name

    reviewer = crud.get_user_by_id(db=db, user_id=reviewer.user_id)

    payload = {
        "replace_original": "true",
        "text": f"Assigned reviewer:{slack_payload.reviewer_name} <@{str(slack_payload.reviewer_slack_id)}>\nTrainee Name: {slack_payload.trainee_name}\nAssessment: {slack_payload.assessment_name}",
    }

    response = requests.post(url=settings.SLACK_BOT_URL, json=payload)
    try:
        response.raise_for_status()
        payload = {
            "number": 1,
            "pull_request": {
            "url": f"https://api.github.com/repos/brn-test-assessment/{repo_name}/pulls/1",
            "head": {
                "sha": "OIJSADJSAODJASJDOJASD",
                },
            },
        "sender": {
            "login": ,
        },
        "comment": {
            "body": "@brnbot confirmReviewer",
        },
        "installation": {
            "id": 26363998,
        },
        "issue": {
            "number": 1,
            "pull_request": {
                "url": f"https://api.github.com/repos/{brn_org_name}/{repo_name}/pulls/1"
            },
        },
        "repository": {
            "owner": {
                "login": "brn-test-assessment",
            },
            "name": repo_name,
        },
    }
        response_ghbot = requests.post(url=settings.GITHUB_BOT_URL, json=)
    except requests.exceptions.HTTPError as e: 
            raise e
    except Exception as e:
            raise e
    return response
