import json
from app import crud
from sqlalchemy.orm import Session
import copy
import requests
from datetime import datetime
from app.dependencies import Settings


def ask_reviewers(
    db: Session,
    assessment_tracker_entry_id: int,
    reviewer_id: int,
    settings: Settings,
):
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db=db, entry_id=assessment_tracker_entry_id)
    assessment_tracker_entry.reviewer_id = reviewer_id
    assessment_tracker_entry.status = "Assigning Reviewer"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    db.add(assessment_tracker_entry)
    db.commit()

    user = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)

    reviewer = crud.get_reviewer_by_id(db=db, reviewer_id=reviewer_id)
    reviewer_slack = crud.get_user_by_id(db=db, user_id=reviewer.user_id)
    
    assessment = crud.get_assessment_by_id(db=db, assessment_id=assessment_tracker_entry.assessment_id)
    filename = 'app/slack_utils/review_request.json'
    with open(filename, 'r') as f:
        data = json.load(f)
        payload = copy.deepcopy(data)
        payload['blocks'][0]['text']['text']=(
            f'Please confirm if you would like to review the assessment for:\nTrainee Name: {user.name}\nAssessment: {assessment.name}')
        payload['blocks'][1]['text']['text']=(f'<@{str(reviewer_slack.slack_id)}>')
        # payload['blocks'][1]['text']['text']=(f"<@{test1_slack_id}>\n")

        response = requests.post(
            url= settings.SLACK_BOT_URL, json=payload
            )

def confirm_reviewer(
    db: Session,
    assessment_name: str,
    response_url: str,
    trainee_name: str,
    slack_id: str,
):  
    trainee = crud.get_user_by_name(db=db, name=trainee_name)
    assessment_entry = crud.get_assessment_tracker_entry_by_user_assessment_name(db=db,
                user_id=trainee.id,
                assessment_name=assessment_name
                )
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db=db, entry_id=assessment_entry.id)
    reviewer = crud.get_reviewer_by_slack_id(db=db, slack_id=slack_id)
    assessment_tracker_entry.reviewer_id = reviewer.id
    assessment_tracker_entry.status = "Reviewer Assigned"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    db.add(assessment_tracker_entry)
    db.commit()

    # user = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)
    # user_name = user.name

    reviewer = crud.get_user_by_id(db=db, reviewer_id=reviewer.user_id)
    
    assessment = crud.get_assessment_by_id(db=db, assessment_id=assessment_tracker_entry.assessment_id)
    assessment_name = assessment.name

    payload = {
    "replace_original": "true",
    "text": f"Assigned reviewer:{reviewer.name} <@{str(slack_id)}>",
    }

    response = requests.post(
            url= response_url, json=payload
            )

