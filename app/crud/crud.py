from datetime import datetime
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
# writing core crud functions for the api endpoints #8 

# create crud functions for `/api/init_assessment`

# create app.crud.verify_member
# takes in gitusername 
# returns bool
def verify_member(db: Session, username: str):
    return db.query(models.Users).filter(models.Users.github_username == username)\
        .with_entities(models.Users.user_id).first()

# create app.crud.init_assessment_tracker
# takes in assessment info and create an entry in assessment_tracker table
def init_assessment_tracker(
    db: Session,
    assessment_tracker: schemas.assessment_tracker_init,
    user_id: int
    ):
    if(assessment_tracker.assessment_id == None):
        assessment_tracker.assessment_id = db.query(models.Assessments).filter(models.Assessments.name == assessment_tracker.name)\
        .with_entities(models.Assessments.assessment_id).scalar()

    db_obj = models.Assessment_Tracker(
        assessment_id=assessment_tracker.assessment_id,
        user_id= user_id,
        latest_commit=assessment_tracker.latest_commit,
        last_updated= datetime.now(),
        log={"Initiated": str(datetime.now())} 
        )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    