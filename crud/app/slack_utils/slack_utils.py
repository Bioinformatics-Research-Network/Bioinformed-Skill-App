import json
from sqlalchemy import true
from app import crud
from sqlalchemy.orm import Session
import copy
import requests
from datetime import datetime


def confirm_reviewer(
    db: Session,
    assessment_tracker_entry_id: int,
    reviewer_id: int,
):
    assessment_tracker_entry = crud.get_assessment_tracker_entry_by_id(db=db, entry_id=assessment_tracker_entry_id)
    assessment_tracker_entry.reviewer_id = reviewer_id
    assessment_tracker_entry.status = "Assigning Reviewer"
    assessment_tracker_entry.last_updated = datetime.utcnow()
    # db.add(assessment_tracker_entry)
    db.commit()

    user = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)
    user_name = user.name

    assessment = crud.get_assessment_by_id(db=db, assessment_id=assessment_tracker_entry.assessment_id)
    assessment_name = assessment.name
    test2_slack_id = "U026THRFP5Z" # james
    test1_slack_id = "U01SCJKF6CD" # anmol
    filename = 'app/slack_utils/review_request.json'
    with open(filename, 'r') as f:
        data = json.load(f)
        payload = copy.deepcopy(data)
        payload['blocks'][0]['text']['text']=(f"{user_name} would like {assessment_name} to be reviewed")
        # payload['blocks'][1]['text']['text']=(f"<@{test1_slack_id}>\n<@{test2_slack_id}>\n<@Uxxxxxxxxxx>")
        payload['blocks'][1]['text']['text']=(f"<@{test1_slack_id}>\n")

        response = requests.post(
            url= "https://hooks.slack.com/services/blahblah", json=payload
            )


# user_name="xxx"
# assessment_name="yyy"
# test2_slack_id = "U026THRFP5Z" # james
# test1_slack_id = "U01SCJKF6CD" # anmol
# filename = 'review_request.json'        
# with open(filename, 'r') as f:
#         data = json.load(f)
#         payload = copy.deepcopy(data)
#         payload['blocks'][0]['text']['text']=(f"{user_name} would like {assessment_name} to be reviewed")
#         payload['blocks'][1]['text']['text']=(f"<@{test1_slack_id}>\n<@{test2_slack_id}>\n<@Uxxxxxxxxxx>")

#         response = requests.post(
#                 url= "https://hooks.slack.com/services/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", json=payload
#             )
        
