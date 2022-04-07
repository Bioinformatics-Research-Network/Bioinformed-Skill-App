from datetime import datetime
import json
from pydantic import Json
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
# writing core crud functions for the api endpoints #8 

# create crud functions for `/api/init_assessment`

# create app.crud.verify_member
# takes in gitusername 
# returns bool
def verify_member(db: Session, username: str):
    return db.query(models.Users)\
        .filter(models.Users.github_username == username)\
        .with_entities(models.Users.user_id, models.Users.first_name).first()

# crud.verify_reviewer -> required when reviewer gives a command. 
# first checks if the reviewer is user then verifies if they are a reviewer
def verify_reviewer(
    db: Session,
    reviewer_username: str
    ):

    reviewer = verify_member(db=db, username=reviewer_username)
    if reviewer is None:
        return None
    reviewer_info = db.query(models.Reviewers)\
        .filter(models.Reviewers.user_id == reviewer.user_id)\
        .with_entities(models.Reviewers.reviewer_id).first()
    if reviewer_info is None:
        return None
    return reviewer_info

def assessment_id_tracker(
    db:Session,
    assessment_name: str
    ):
    return db.query(models.Assessments)\
        .filter(models.Assessments.name == assessment_name)\
        .with_entities(models.Assessments.assessment_id).scalar()
# create app.crud.init_assessment_tracker
# takes in assessment info and create an entry in assessment_tracker table
def init_assessment_tracker(
    db: Session,
    assessment_tracker: schemas.assessment_tracker_init,
    user_id: int
    ):
    
    assessment_id = assessment_id_tracker(
        db=db, 
        assessment_name=assessment_tracker.assessment_name
        )

    db_obj = models.Assessment_Tracker(
        assessment_id=assessment_id,
        user_id= user_id,
        latest_commit=assessment_tracker.latest_commit,
        last_updated= datetime.utcnow(),
        status="Initiated",
        log=[{"Status":"Initiated","Updated":str(datetime.utcnow()), "Commit":assessment_tracker.latest_commit}]
        )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
    
# app.crud.check_pre_req

# crud.approve_assessment
# update status and log

def approve_assessment(
    db: Session,
    user_id: int,
    # reviewer_id: int, # use this to check if the reviewer is correct for the given assessment tracker
    # will be used when reviewers are assigned and updated in DB 
    assessment_name: str
    ):
    assessment_id = assessment_id_tracker(
        db=db,
        assessment_name= assessment_name
        )
    
    # first read the data which is to be updated

    approve_assessment_data = db.query(models.Assessment_Tracker)\
        .filter(models.Assessment_Tracker.user_id == user_id,  
        models.Assessment_Tracker.assessment_id == assessment_id).first()

    if approve_assessment_data is None:
        return None

    approve_assessment_data.status = "Approved"
    approve_assessment_data.last_updated = datetime.utcnow()
    log = {"Updated": datetime.utcnow(), "Status" : "Approved"}
    approve_assessment_data.log.append(log)

    db.add(approve_assessment_data)
    db.commit()
    db.refresh(approve_assessment_data)
    
    return approve_assessment_data


# app.crud.update_assessment_log
# invoked by /api/update
# input: logs of GHA, assessment_tracker info

def update_assessment_log(
    db: Session,
    logs: schemas.logs,
    asses_track_info: schemas.check_update
    ):
    assessment_id = assessment_id_tracker(
        db=db,
        assessment_name= asses_track_info.assessment_name
        )
    
    user = verify_member(db=db, username=asses_track_info.github_username)
    if user is None:
        return None
    # first read the data which is to be updated

    assess_track_data =  db.query(models.Assessment_Tracker)\
        .filter(models.Assessment_Tracker.user_id == user.user_id,
        models.Assessment_Tracker.assessment_id == assessment_id)\
        .with_entities(models.Reviewers.reviewer_id).first()

    if assess_track_data is None:
        return None

    assess_track_data.last_updated = datetime.utcnow()
    assess_track_data.log.append(logs.logs)

    db.add(assess_track_data)
    db.commit()
    db.refresh(assess_track_data)
    
    return assess_track_data
