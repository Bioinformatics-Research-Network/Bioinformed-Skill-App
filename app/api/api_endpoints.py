import copy
from datetime import datetime
from urllib import response
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.api.services import get_db
from app import schemas, crud, utils, config


## TODO: Fix this later -- should be parameterized using fastapi config
badgr_config = config.badgr_config_test


router = APIRouter(prefix="/api", tags=["api"])


# the endpoints are defined according to:
# https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#


@router.post("/register", response_model=schemas.RegisterResponse)
def register(
    *, register_request: schemas.RegisterRequest, db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    try:
        crud.create_user(db, register_request=register_request)
        # Notify the user that they have been registered
        utils.register_notify(
            register_request.email,
            register_request.first_name,
            register_request.last_name,
            register_request.github_username,
        )
    except IntegrityError:
        # Notify the user that they have been registered
        utils.register_notify(
            register_request.email,
            register_request.first_name,
            register_request.last_name,
            register_request.github_username,
        )
        raise HTTPException(
            status_code=422,
            detail="User with this email already exists in the system",
        )
    except Exception as e:  # pragma: no cover
        print("Other error:\n" + str(e))
        raise HTTPException(
            status_code=500,
            detail="An uncaught error occurred registering the user:\n" + str(e),
        )

    return schemas.RegisterResponse(registered=True)


@router.post("/init", response_model=schemas.InitResponse)
def init(*, db: Session = Depends(get_db), init_request: schemas.InitRequest):
    """
    Initiates new assessment instances for assessment_tracker table.

    :param db: Generator for Session of database
    :param init_request: Pydantic request model schema used by `/api/init` endpoint

    :returns: Json indicating if assessment was initiated, first name of user for bot use

    :raises: HTTPException 422 if:
        - Entry already exists
        - User does not exist
        - Assessment does not exist
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
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    # bool signifies if the assessment tracker entry was initialized as well as that the member is valid
    return {"Initiated": True, "User_first_name": user.first_name}


@router.get("/view")
def view(*, db: Session = Depends(get_db), view_request: schemas.ViewRequest):
    """
    Returns the assessment tracker entry for the given user and assessment as a json object.

    :param db: Generator for Session of database
    :param view_request: Pydantic request model schema used by `/api/view` endpoint

    :returns: Json object containing the assessment tracker entry for the given user and assessment

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
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
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return assessment_tracker_entry.as_dict()


@router.patch("/update")
def update(*, db: Session = Depends(get_db), update_request: schemas.UpdateRequest):
    """
    Updates the assessment tracker entry for the given user and assessment with the given commit and log.

    :param db: Generator for Session of database
    :param update_request: Pydantic request model schema used by `/api/update` endpoint

    :returns: Json object indicating if the assessment tracker entry was updated

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
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
            latest_commit=update_request.latest_commit,
            update_logs=copy.deepcopy(update_request.log),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return {"Logs Updated": True}


@router.post("/delete")
def delete(*, db: Session = Depends(get_db), view_request: schemas.DeleteRequest):
    """
    Deletes the assessment tracker entry for the given user and assessment.

    :param db: Generator for Session of database
    :param view_request: Pydantic request model schema used by `/api/delete` endpoint

    :returns: Json object indicating if the assessment tracker entry was deleted

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
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
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return {"Entry deleted": True}


@router.post("/check")
def check(*, db: Session = Depends(get_db), check_request: schemas.CheckRequest):
    """
    Run automated checks on the assessment tracker entry for the given user and assessment.

    :param db: Generator for Session of database
    :param check_request: Pydantic request model schema used by `/api/check` endpoint

    :returns: Json object indicating if the assessment tracker entry was checked

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
    """
    try:
        assessment_tracker_entry = crud.get_assessment_tracker_entry_by_commit(
            db=db, commit=check_request.latest_commit
        )
        if assessment_tracker_entry.status == "Approved":
            raise ValueError("Assessment already approved")
        update_logs = {
            "timestamp": str(datetime.utcnow()),
            "checks_passed": check_request.passed,
            "commit": check_request.latest_commit,
        }
        crud.update_assessment_log(
            db=db,
            assessment_tracker_entry_id=assessment_tracker_entry.entry_id,
            latest_commit=check_request.latest_commit,
            update_logs=copy.deepcopy(update_logs),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return {"Check": True}


@router.post("/review", response_model=schemas.ReviewResponse)
def review(*, db: Session = Depends(get_db), review_request: schemas.ReviewRequest):
    """
    Assign the assessment tracker entry for the given user and assessment to a reviewer.

    :param db: Generator for Session of database
    :param review_request: Pydantic request model schema used by `/api/review` endpoint

    :returns: Json object containing the reviewer info

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
        - Assessment tracker entry is already approved
        - Assessment tracker entry is already assigned to a reviewer
        - This assessment is not passing automated checks
        - The commit is not found in the assessment tracker entry table
    """
    try:
        assessment_tracker_entry = crud.get_assessment_tracker_entry_by_commit(
            db=db, commit=review_request.latest_commit
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
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))

    return reviewer_info


@router.patch("/approve")
def approve(*, db: Session = Depends(get_db), approve_request: schemas.ApproveRequest):
    """
    Approve the assessment tracker entry for the given user and assessment.

    :param db: Generator for Session of database
    :param approve_request: Pydantic request model schema used by `/api/approve` endpoint

    :returns: Json object indicating if the assessment tracker entry was approved

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
        - Assessment tracker entry is already approved
        - Assessment tracker entry is not assigned to a reviewer
        - Assessment tracker entry is not passing automated checks
        - The commit is not found in the assessment tracker entry table
        - The reviewer is not found in the reviewer table
        - The reviewer is the same as the user
        - The reviewer is not listed as a reviewer for this assessment
    """
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
    except KeyError as e:  # pragma: no cover
        msg = "Badgr: Unable to locate assessment: " + str(e)
        raise HTTPException(status_code=500, detail=msg)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {"Assessment Approved": True}


# to be done
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status
# updates required: app.crud.check_pre_req?
