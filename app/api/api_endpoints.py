# starting with api endpoints : these may be divided into different files when needed.
from http.client import HTTPException
from fastapi import APIRouter, Depends
from pydantic import Json
from sqlalchemy.orm import Session
from .services import get_db
from app.crud import crud
from app.schemas import schemas
from app.utils import utils

router = APIRouter(
    prefix="/api",
    tags=["api"]
)

# ignore errors during the development, 
# these will be solved as schemas and crud functions will be made
# the endpoints are defined according to: 
# https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#


# /api/init-assessment : needs gitusername and assessment_tracker details
# uses: invoked by bot.assessment_init
# app.crud.verify_member # takes in username returns bool # returns userid
# app.crud.initialize_assessment_tracker:
# initialize assessment, uses username/userid and assessment data like assessment id and commit
# returns bool : True if member verified and assessment initialized

# updates required: app.crud.check_pre_req
@router.post("/init_assessment")
def init_assessment(*,
    db: Session = Depends(get_db),
    # for app.crud.verify_member
    # make request schemas which accepts gitusername
    user: schemas.user_check,
    # for app.crud.init_assessment_tracker
    # make schemas which takes in commit, assessment detail
    assessment_tracker: schemas.assessment_tracker_init
    ):
    check_user = crud.verify_member(db=db, username=user.github_username) # returns data of the user

    if (check_user == None):
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.init_assessment_tracker(
            db=db,
            assessment_tracker=assessment_tracker,
            user_id=check_user.user_id
    )
     # bool signifies if the assessment tracker was initialized
     # as well as that the member is valid
    return {"Initiated": True, "User_first_name":check_user.first_name}

# /api/verify-member : I think endpoints should not be explicitly be made if a simple function can replace it. And it is not explicitly used anywhere.
#        not needed necessarly can be replaced by app.crud.verify_member

# /api/init-check: 
# invoked by bot.check
# uses:
#   1. app.crud.verify_member
#   2. app.utils.runGHA
#   3. /api/update: api.update()
# will make later when app.utils are made
# working on it
@router.post("/init_check")
def init_check(*,
    db: Session = Depends(get_db),
    asses_track_info: schemas.check_update
    ):
    verify_user = crud.verify_member(
        db=db,
        username=asses_track_info.github_username
        )
    if verify_user == None:
        raise HTTPException(status_code=404, detail="User Not Registered")

    log = utils.runGHA(db=db, check=asses_track_info) 
    logs = schemas.logs(logs=log) 

    update(db=db, logs=logs, update=asses_track_info)

    return {"Logs updated"}

# /api/update:
# invoked by bot.check
# uses: app.crud.update_assessment_log
# updates the log in assessment_tracker table
# working on it
@router.patch("/update")
def update(*,
    db: Session = Depends(get_db),
    logs: schemas.logs,
    asses_track_info: schemas.check_update
    ):
    crud.update_assessment_log(
        db=db,
        logs=logs,
        asses_track_info=asses_track_info
        )

    return {"Logs Updated"}

# /api/approve-assessment
# invoked by bot.approve
# uses: crud.approve_assessment : update status and log
# working
@router.patch("/approve_assessment")
def approve_assessment(*,
    db: Session = Depends(get_db),
    approve_assessment: schemas.approve_assessment
    ):
    user = crud.verify_member(db=db, username=approve_assessment.member_username)
    reviewer = crud.verify_reviewer(db=db, reviewer_username=approve_assessment.reviewer_username)
    if(user == None or reviewer == None):
        raise HTTPException(status_code=404, detail="User/Reviewer Not Found")
    
    assessment_status = crud.approve_assessment(
        db=db,
        user_id=user.user_id,
        reviewer_id=reviewer.reviewer_id, 
        assessment_name=approve_assessment.assessment_name
     )
    if assessment_status == None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # app.utils.sync_badger 

    return {"Assessment Approved"}



# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status
# testing poetry local env