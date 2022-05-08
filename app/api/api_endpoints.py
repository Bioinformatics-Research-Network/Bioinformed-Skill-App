from app.crud.crud import get_assessment_tracker_entry_by_commit
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .services import get_db
from app import schemas, crud, utils

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
    # Try to init assessment tracker
    # If member is not valid, raise 422 error
    # If other error occurs, raise 500 error
    try:
        user = crud.get_user(db=db, username=user.github_username)
        res = crud.init_assessment_tracker(
            db=db, assessment_tracker=assessment_tracker, user_id=user.user_id
        )
        print(res)
    except ValueError as e:
        print("ValueError:", e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # bool signifies if the assessment tracker entry was initialized as well as that the member is valid
    return {"Initiated": True, "User_first_name": user.first_name}


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
    try:
        user = crud.get_user_by_username(db=db, username=asses_track_info.github_username)
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=asses_track_info.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.user_id,
            assessment_id=assessment.assessment_id,
        ) # Get assessment tracker id
        update_logs = utils.runGHA(check=asses_track_info) # Run GHA checks
        crud.update_assessment_log(
            db=db,
            assessment_tracker_id=assessment_tracker_entry.assessment_tracker_id,
            latest_commit=asses_track_info.latest_commit, 
            update_logs=update_logs.log
        ) # Update logs
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"Logs updated": "init-check"}


@router.post("/init_review")
def init_review(
    *, db: Session = Depends(get_db), payload: schemas.init_review
):
    """
    Invoked by bot.review

    :param db: Generator for Session of database
    :param asses_track_info: inputs user github username, assessment name and latest commit.

    :returns: Json indicating logs were updated
    """ 
    try:
        assessment_tracker_entry = get_assessment_tracker_entry_by_commit(
            db=db, commit=payload.commit
        ) # Get assessment tracker id
        verify_check = crud.verify_check(
            db=db, 
            assessment_tracker_entry_id=assessment_tracker_entry.entry_id
        )
        if not verify_check:
            raise ValueError("Automated check not passed for latest commit")
        update_logs = utils.get_reviewer(
            db=db, assessment_tracker_entry_id=assessment_tracker_entry.entry_id
        ) # Run GHA checks
        crud.update_assessment_log(
            db=db,
            assessment_tracker_id=assessment_tracker_entry.assessment_tracker_id,
            latest_commit=asses_track_info.latest_commit, 
            update_logs=update_logs.log
        ) # Update logs
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    update_logs = utils.get_reviewer()

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
    try:
        crud.update_assessment_log(
            db=db, asses_track_info=asses_track_info, update_logs=update_logs.log
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

    # Approve assessment
    try:
        user = crud.verify_member(db=db, username=approve_assessment.member_username)
        reviewer = crud.verify_reviewer(
            db=db, reviewer_username=approve_assessment.reviewer_username
        )
        if verify_reviewer:
            reviewer_id 
            assessment_status = crud.approve_assessment_crud(
                db=db,
                user_id=user.user_id,
                # reviewer_id=reviewer.reviewer_id,  # will be use when reviewers are assigned
                assessment_name=approve_assessment.assessment_name,
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # app.utils.badgr_utils implementation to be done here

    return {"Assessment Approved": True}






# to be done
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status
# updates required: app.crud.check_pre_req?
