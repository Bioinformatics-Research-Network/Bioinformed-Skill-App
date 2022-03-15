# to create random data and test other crud utils
from sqlalchemy.orm import Session
from app.models.models import Users
from app.schemas.users import UserCreate
from app import models
from app.utils import utils

def random_user(): # creates random user info
    first, last = utils.random_name()
    username = utils.random_username(first,last)
    email = utils.random_rmail(username)
    random_usr = UserCreate(
        github_username=username, 
        first_name=first,
        last_name=last,
        email=email
        )
    return random_usr   


def create_random_user( 
     db: Session,
     obj_in: UserCreate): # commit random users in DB
    
    db_obj = Users(
            email=obj_in.email,
            github_username=obj_in.github_username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name
        )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
    
