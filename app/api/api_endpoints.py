# starting with api endpoints : these may be divided into different files when needed.
from fastapi import APIRouter
from sqlalchemy.orm import Session
from .services import get_db

router = APIRouter(
    prefix="/api",
    tags=["api"]
)

# ignore errors during the development, these will be solved as schemas and crud functions will be made
# the endpoints are defined according to: 
# https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#


# /api/init-assessment : needs gitusername and assessment_tracker details
# uses: invoked by bot.assessment_init
# app.crud.verify_member # takes in username returns bool # returns userid
# app.crud.initialize_assessment_tracker:
#     initialize assessment , uses username/userid and assessment data like assessment id and commit
# returns bool : True if member verified and assessment initialized
@router.post("/init-assessment")
def init_assessment(
    db=Session = Depends(get_db),
    # for app.crud.verify_member
    # make schemas which accepts gitusername
    user: schemas.user_check 
    # for app.crud.init_assessment_tracker
    # make schemas which takes in commit, assessment detail
    assessment_tracker: schemas.assessment_tracker_init 
):
    check_user = app.crud.verify_member(user) # returns bool

    if (check_user):
        app.crud.init_assessment_tracker(assessment_tracker)
    
     # bool signifies if the assessment tracker was initialized
     # as well as that the member is valid
    return check_user

# /api/verify-member : I think endpoints should not be explicitly be made if a simple function can replace it.
#        not needed necessarly can be replaced by app.crud.verify_member


# /api/init-check: 

# /api/update
# /api/approve-assessment
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status