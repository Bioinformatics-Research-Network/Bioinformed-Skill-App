from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .services import get_db
from app.crud import crud
from app.schemas import schemas
from app.utils import utils

router = APIRouter(prefix="/api", tags=["api"])


# the endpoints are defined according to:
# https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#


@router.post("/init_assessment", response_model=schemas.response_init_assessment)
def init_assessment(
    *,
    db: Session = Depends(get_db),
    user: schemas.user_check,
    assessment_tracker: schemas.assessment_tracker_init
    ):
    """
    Invoked by bot.assessment_init
    Initiates new assessments for assessment_tracker table. 
    It verifies member by github username if valid, initiates
    
    :param db: Generator for Session of database
    :param user: Inputs user's github username.
    :param assessment_tracker: Inputs assessment name and latest commit.

    :returns: Json indicating if assessment was initiated, first name of user for bot use
    """
    check_user = crud.verify_member(db=db, username=user.github_username)

    if check_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    assessment_init = crud.init_assessment_tracker(
        db=db, assessment_tracker=assessment_tracker, user_id=check_user.user_id
    )
    if assessment_init is None:
        raise HTTPException(status_code=404, detail="Invalid Assessment name")

    # bool signifies if the assessment tracker entry was initialized as well as that the member is valid
    return {"Initiated": True, "User_first_name": check_user.first_name}



@router.post("/init_check")
def init_check(
    *, db: Session = Depends(get_db), asses_track_info: schemas.check_update
    ):
    """
    Invoked by bot.check
    Verifies member github username, then provokes utils.runGHA to run GHA checks on the commit.
    Updates the logs of assessment_tracker entry with updated logs from GHA through api.update()

    :param db: Generator for Session of database
    :param asses_track_info: inputs user github username, assessment name and latest commit.

    :returns: Json indicating logs were updated
    """
    verify_user = crud.verify_member(db=db, username=asses_track_info.github_username)
    if verify_user is None:
        raise HTTPException(status_code=404, detail="User Not Registered")

    update_logs = utils.runGHA(check=asses_track_info)

    update(db=db, asses_track_info=asses_track_info, update_logs=update_logs)

    return {"Logs updated": "init-check"}



@router.patch("/update")
def update(
    *,
    db: Session = Depends(get_db),
    asses_track_info: schemas.check_update,
    update_logs: schemas.update_log
    ):
    """
    Invoked by bot.check and /api/init-check
    Updates the log of the assessment_tracker table entry with input log.

    :param db: Generator for Session of database
    :param asses_track_info: inputs user github username, assessment name and latest commit.
    :param update_logs: inputs the logs which will be added to pre-existing log entry. 

    :returns: json indicating the logs were updated
    """
    assessment_log = crud.update_assessment_log(
        db=db, asses_track_info=asses_track_info, update_logs=update_logs.log
    )
    if assessment_log is None:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {"Logs Updated": "update"}



@router.patch("/approve_assessment")
def approve_assessment(
    *, db: Session = Depends(get_db), approve_assessment: schemas.approve_assessment
    ):
    """
    Invoked by bot.ipprove
    Changes the status of the assessment_tracker entry to "Approved", 
    updates the logs with the changes made
    Verifies member and reviewer. 
    
    Implements app.utils.badgr_utils functions to assign badges to the user if assessment is approved.

    :param db: Generator for Session of database
    :param approve_assessment: inputs member and reviewer github username and assessment name.

    :returns: json indicating if the assessment was approved as a bool.
    """
    user = crud.verify_member(db=db, username=approve_assessment.member_username)
    reviewer = crud.verify_reviewer(
        db=db, reviewer_username=approve_assessment.reviewer_username
    )
    if user is None or reviewer is None:
        raise HTTPException(status_code=404, detail="User/Reviewer Not Found")

    if approve_assessment.member_username == approve_assessment.reviewer_username:
        raise HTTPException(
            status_code=403,
            detail="Reviewer not authorized to review personal assessments",
        )

    assessment_status = crud.approve_assessment_crud(
        db=db,
        user_id=user.user_id,
        # reviewer_id=reviewer.reviewer_id,  # will be use when reviewers are assigned
        assessment_name=approve_assessment.assessment_name,
    )
    if assessment_status is None:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # app.utils.badgr_utils implementation to be done here

    return {"Assessment Approved": True}


# to be done
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status
# updates required: app.crud.check_pre_req?
