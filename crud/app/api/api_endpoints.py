import copy
from datetime import datetime
import hashlib
from requests import request
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import Settings
from app import crud, utils
import app.api.schemas as schemas
from app.dependencies import get_db, get_settings

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/init")
def init(
    *,
    db: Session = Depends(get_db),
    init_request: schemas.InitRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Initiates new assessment instances for assessment_tracker table.

    :param db: Generator for Session of database
    :param init_request: Pydantic request model schema used by `/api/init` endpoint

    :returns: Json indicating if assessment was initiated, first name of user

    :raises: HTTPException 422 if:
        - Entry already exists
        - User does not exist
        - Assessment does not exist
    """
    # Try to init assessment tracker
    # If member is not valid, raise 422 error
    # If other error occurs, raise 500 error
    try:
        print("creating assessment tracker")
        crud.create_assessment_tracker_entry(
            db=db,
            user_id=init_request.user_id,
            assessment_id=init_request.assessment_id,
            commit=hashlib.sha1(
                (
                    str(datetime.now()).encode("utf-8")
                    + str(init_request.user_id).encode("utf-8")
                    + str(init_request.assessment_id).encode("utf-8")
                )
            ).hexdigest(),
        )
        print("assessment tracker created")
    except ValueError as e:
        print(e)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    # Use the bot to set up the assessment on GitHub
    try:
        print("setting up assessment")
        assessment = crud.get_assessment_by_id(
            db=db, assessment_id=init_request.assessment_id
        )
        user = crud.get_user_by_id(db=db, user_id=init_request.user_id)
        payload = {
            "name": assessment.name,
            "install_id": int(assessment.install_id),
            "repo_prefix": assessment.repo_prefix,
            "github_org": assessment.github_org,
            "username": user.username,
            "template_repo": assessment.template_repo,
            "latest_release": assessment.latest_release,
            "review_required": assessment.review_required == 1,
        }
        print("Sending request to bot init")
        response = request(
            "POST",
            f"{settings.GITHUB_BOT_URL}/init",
            json=payload,
        )
        print("Bot responded")
        response.raise_for_status()
    except Exception as e:  # pragma: no cover
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    # Update the assessment tracker with the GitHub URL
    try:
        print("Updating assessment tracker")
        crud.update_assessment_tracker_entry(
            db=db,
            user_id=user.id,
            assessment_id=assessment.id,
            github_url=response.json()["github_url"],
            status="Initiated",
            commit=response.json()["latest_commit"],
        )
        print("Assessment tracker updated")
    except Exception as e:  # pragma: no cover
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    crud.get_assessment_tracker_entry(
        db=db, user_id=user.id, assessment_id=assessment.id
    )

    # bool signifies if the assessment tracker entry was initialized as well as that the
    # member is valid
    return True


@router.get("/view")
def view(*, db: Session = Depends(get_db), view_request: schemas.ViewRequest):
    """
    Returns the assessment tracker entry for the given user and assessmen
    t as a json object.

    :param db: Generator for Session of database
    :param view_request: Pydantic request model schema used by
    `/api/view` endpoint

    :returns: Json object containing the assessment tracker entry for the given
     user and assessment

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
    """
    try:
        user = crud.get_user_by_username(db=db, username=view_request.username)
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=view_request.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.id,
            assessment_id=assessment.id,
        )
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return assessment_tracker_entry.__dict__


@router.patch("/update")
def update(
    *, db: Session = Depends(get_db), update_request: schemas.UpdateRequest
):
    """
    Updates the assessment tracker entry for the given user and assessment with the
    given commit and log.

    :param db: Generator for Session of database
    :param update_request: Pydantic request model schema used by `/api/update` endpoint

    :returns: Json object indicating if the assessment tracker entry was updated

    :raises: HTTPException 422 if:
        - User does not exist
        - Assessment does not exist
        - Assessment tracker entry does not exist
    """
    try:

        user = crud.get_user_by_username(
            db=db, username=update_request.username
        )
        assessment = crud.get_assessment_by_name(
            db=db, assessment_name=update_request.assessment_name
        )
        assessment_tracker_entry = crud.get_assessment_tracker_entry(
            db=db,
            user_id=user.id,
            assessment_id=assessment.id,
        )
        crud.update_assessment_log(
            db=db,
            entry_id=assessment_tracker_entry.id,
            latest_commit=update_request.latest_commit,
            status=update_request.status,
            update_logs=copy.deepcopy(update_request.log),
        )
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {"Logs Updated": True}


@router.post("/delete")
def delete(
    *,
    db: Session = Depends(get_db),
    delete_request: schemas.DeleteAssessmentTrackerRequest,
    settings: Settings = Depends(get_settings),
):
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
        crud.delete_assessment_tracker_entry(
            db=db,
            delete_request=delete_request,
            settings=settings,
        )
    except ValueError as e:
        print(str(e))
        db.rollback()
        print("rollback")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        db.rollback()
        print("rollback")
        raise HTTPException(status_code=500, detail=str(e))

    return {"Entry deleted": True}


@router.post("/check")
def check(
    *, db: Session = Depends(get_db), check_request: schemas.CheckRequest
):
    """
    Run automated checks on the assessment tracker entry for the
    given user and assessment.

    :param db: Generator for Session of database
    :param check_request: Pydantic request model schema used by
    `/api/check` endpoint

    :returns: Json object indicating if the assessment tracker entry
    was checked

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
            entry_id=assessment_tracker_entry.id,
            latest_commit=check_request.latest_commit,
            update_logs=copy.deepcopy(update_logs),
        )
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    # Get the assessment table entry
    assessment = crud.get_assessment_by_id(
        db=db, assessment_id=assessment_tracker_entry.assessment_id
    )
    return {"Check": True, "review_required": assessment.review_required == 1}


@router.post("/review", response_model=schemas.ReviewResponse)
def review(
    *, db: Session = Depends(get_db), review_request: schemas.ReviewRequest,
    settings: Settings = Depends(get_settings),
):
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
            db=db, assessment_tracker_entry=assessment_tracker_entry,
            settings=settings
        )
        reviewer_user = crud.get_user_by_id(db=db, user_id=reviewer.user_id)
        reviewer_info = {
            "reviewer_id": reviewer.id,
            "reviewer_username": reviewer_user.username,
        }
        crud.assign_reviewer(
            db=db,
            assessment_tracker_entry=assessment_tracker_entry,
            reviewer_info=reviewer_info,
        )
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return reviewer_info


@router.patch("/approve")
def approve(
    *,
    db: Session = Depends(get_db),
    approve_request: schemas.ApproveRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Approve the assessment tracker entry for the
    given user and assessment.

    :param db: Generator for Session of database
    :param approve_request: Pydantic request model schema used
    by `/api/approve` endpoint

    :returns: Json object indicating if the assessment tracker
    entry was approved

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
        assessment_tracker_entry = crud.get_assessment_tracker_entry_by_commit(
            db=db, commit=approve_request.latest_commit
        )
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    orig_status = copy.deepcopy(assessment_tracker_entry.status)
    try:
        # Get the trainee info
        user = crud.get_user_by_id(
            db=db, user_id=assessment_tracker_entry.user_id
        )
        # Get the assessment info
        assessment = crud.get_assessment_by_id(
            db=db, assessment_id=assessment_tracker_entry.assessment_id
        )
        if assessment.review_required == 1:
            # Get the reviewer info; error if not exists
            reviewer = crud.get_reviewer_by_username(
                db=db, username=approve_request.reviewer_username
            )
        else:
            reviewer = None
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
        bt = utils.get_bearer_token(settings)
        resp = utils.issue_badge(
            user_email=user.email,
            user_first=user.first_name,
            user_last=user.last_name,
            assessment_name=assessment.name,
            bearer_token=bt,
            config=settings,
        )
        resp.raise_for_status()
        # Add assertion to database
        crud.add_assertion(
            db=db,
            entry_id=assessment_tracker_entry.id,
            assertion=resp.json()["result"][0],
        )
    except KeyError as e:  # pragma: no cover
        print(str(e))
        msg = "Badgr: Unable to locate assessment: " + str(e)

        # If any error, revert status to original
        assessment_tracker_entry.status = orig_status
        db.commit()

        raise HTTPException(status_code=500, detail=msg)
    except ValueError as e:
        print(str(e))

        # If any error, revert status to original
        assessment_tracker_entry.status = orig_status
        db.commit()

        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:  # pragma: no cover
        print(str(e))

        # If any error, revert status to original
        assessment_tracker_entry.status = orig_status
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))

    return {"Assessment Approved": True}


@router.post("/user/delete")
def delete_user(
    *,
    db: Session = Depends(get_db),
    delete_request: schemas.DeleteUserRequest,
    settings: Settings = Depends(get_settings),
):
    """
    Deletes all info for a user.

    :param db: Generator for Session of database
    :param view_request: Pydantic request model schema used by `/api/delete` endpoint

    :returns: Json object indicating if the assessment tracker entry was deleted

    :raises: HTTPException 422 if:
        - User does not exist
    """
    try:
        crud.delete_user(
            db=db, user_id=delete_request.user_id, settings=settings
        )
    except Exception as e:  # pragma: no cover
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {"User deleted": True}


# to be done
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status
# updates required: app.crud.check_pre_req?
