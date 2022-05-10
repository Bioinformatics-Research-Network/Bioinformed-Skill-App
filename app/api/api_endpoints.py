from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.services import get_db
from app import schemas, crud, utils


## TODO: Fix this later -- should be parameterized
badgr_config = utils.config_test


router = APIRouter(prefix="/api", tags=["api"])


# the endpoints are defined according to:
# https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#


@router.post("/init", response_model=schemas.InitResponse)
def init(*, db: Session = Depends(get_db), init_request: schemas.InitRequest):
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
        user = crud.get_user_by_username(db=db, username=init_request.github_username)
        crud.init_assessment_tracker(
            db=db, init_request=init_request, user_id=user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    # bool signifies if the assessment tracker entry was initialized as well as that the member is valid
    return {"Initiated": True, "User_first_name": user.first_name}


@router.get("/view")
def view(*, db: Session = Depends(get_db), view_request: schemas.ViewRequest):
    """
    Invoked by bot.approve
    Changes the status of the assessment_tracker entry to "Approved",
    updates the logs with the changes made
    Verifies member and reviewer.

    Implements app.utils.badgr_utils functions to assign badges to the user if assessment is approved.

    :param db: Generator for Session of database
    :param approve_assessment: inputs member and reviewer github username and assessment name.

    :returns: json indicating if the assessment was approved as a bool.
    """
    try:
        user = crud.get_user_by_username(db=db, username=view_request.github_username)
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=view_request.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.user_id,
            assessment_id=assessment.assessment_id,
        )
    except ValueError as e: 
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return assessment_tracker_entry.as_dict()


@router.patch("/update")
def update(*, db: Session = Depends(get_db), update_request: schemas.UpdateRequest):
    """
    Invoked by bot.check -> HTTP request to /api/check
    Updates the log of the assessment_tracker table entry with input log.

    :param db: Generator for Session of database
    :param asses_track_info: inputs user github username, assessment name and latest commit.
    :param update_logs: inputs the logs which will be added to pre-existing log entry.

    :returns: json indicating the logs were updated
    """
    try:
        user = crud.get_user_by_username(db=db, username=update_request.github_username)
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=update_request.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.user_id,
            assessment_id=assessment.assessment_id,
        )
        crud.update_assessment_log(
            db=db,
            assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
            latest_commit=update_request.commit,
            update_logs=update_request.log,
        )
    except ValueError as e: 
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return {"Logs Updated": "update"}


@router.post("/delete")
def delete(*, db: Session = Depends(get_db), view_request: schemas.DeleteRequest):
    """
    Invoked by bot.approve
    Changes the status of the assessment_tracker entry to "Approved",
    updates the logs with the changes made
    Verifies member and reviewer.

    Implements app.utils.badgr_utils functions to assign badges to the user if assessment is approved.

    :param db: Generator for Session of database
    :param approve_assessment: inputs member and reviewer github username and assessment name.

    :returns: json indicating if the assessment was approved as a bool.
    """
    try:
        user = crud.get_user_by_username(db=db, username=view_request.github_username)
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=view_request.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.user_id,
            assessment_id=assessment.assessment_id,
        )
        db.delete(assessment_tracker_entry)
        db.commit()
    except ValueError as e: 
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return True


@router.post("/check")
def check(*, db: Session = Depends(get_db), check_request: schemas.CheckRequest):
    """
    Invoked by bot.check
    Verifies member github username, then provokes utils.runGHA to run GHA checks on the commit.
    Updates the logs of assessment_tracker entry with updated logs from GHA through api.update()

    :param db: Generator for Session of database
    :param asses_track_info: inputs user github username, assessment name and latest commit.

    :returns: Json indicating logs were updated
    """
    try:
        user = crud.get_user_by_username(db=db, username=check_request.github_username)
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=check_request.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.user_id,
            assessment_id=assessment.assessment_id,
        )
        if assessment_tracker_entry.status == "Approved":
            raise ValueError("Assessment already approved")
        update_logs = utils.run_gha(commit=check_request.latest_commit)
        crud.update_assessment_log(
            db=db,
            assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
            latest_commit=check_request.latest_commit,
            update_logs=update_logs,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return {"Logs updated": "check"}


@router.post("/review")
def review(*, db: Session = Depends(get_db), review_request: schemas.ReviewRequest):
    """
    Invoked by bot.review

    :param db: Generator for Session of database
    :param asses_track_info: inputs user github username, assessment name and latest commit.

    :returns: Json indicating logs were updated
    """
    try:
        assessment_tracker_entry = crud.get_assessment_tracker_entry_by_commit(
            db=db, commit=review_request.commit
        )
        if assessment_tracker_entry.status != "Initiated":
            raise ValueError(
                "Assessment tracker entry already under review or approved"
            )
        verify_check = utils.verify_check(
            assessment_tracker_entry=assessment_tracker_entry
        )
        if not verify_check:
            raise ValueError("Automated checks not passed for latest commit")

        reviewer = crud.select_reviewer(
            db=db, assessment_tracker_entry=assessment_tracker_entry
        )
        reviewer_user = crud.get_user_by_id(db=db, user_id=reviewer.user_id)
        reviewer_info = {
            "reviewer_id": reviewer.reviewer_id,
            "reviewer_username": reviewer_user.github_username,
        }
        crud.assign_reviewer(
            db=db,
            assessment_tracker_entry=assessment_tracker_entry,
            reviewer_info=reviewer_info,
        )
    except ValueError as e: 
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return reviewer_info


@router.patch("/approve")
def approve(*, db: Session = Depends(get_db), approve_request: schemas.ApproveRequest):
    """
    Invoked by bot.approve
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
        # Get the assessment_tracker entry
        assessment_tracker_entry = crud.get_assessment_tracker_entry_by_commit(
            db=db, commit=approve_request.latest_commit
        )
        # Get the trainee info
        user = crud.get_user_by_id(db=db, user_id=assessment_tracker_entry.user_id)
        # Get the reviewer info; error if not exists
        reviewer = crud.get_reviewer_by_username(
            db=db, username=approve_request.reviewer_username
        )
        # Get the assessment info
        assessment = crud.get_assessment_by_id(
            db=db, assessment_id=assessment_tracker_entry.assessment_id
        )
        # Approve assessment, update logs, issue badge
        # Error if reviewer is not the one assigned;
        # Error if checks are not passed
        # Error if assessment is already approved;
        # Error if reviewer is same as trainee
        crud.approve_assessment(
            db=db,
            trainee=user,
            reviewer=reviewer,
            reviewer_username=approve_request.reviewer_username,
            assessment=assessment,
        )
        # Issue badge
        bt = utils.get_bearer_token(badgr_config)
        utils.issue_badge(
            user_email=user.email,
            user_first=user.first_name,
            user_last=user.last_name,
            assessment_name=assessment.name,
            bearer_token=bt,
            config=badgr_config,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e: # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return {"Assessment Approved": True}


# to be done
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status
# updates required: app.crud.check_pre_req?
