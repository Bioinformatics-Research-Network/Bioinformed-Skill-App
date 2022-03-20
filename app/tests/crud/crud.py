# to create random data and test other crud utils
from sqlalchemy.orm import Session
from app.models.models import *
from app.tests.utils import utils


def create_random_user( random_users: int, # number of random users to create
     db: Session): # commit random users in DB
    
    for i in range(random_users):
        first, last = utils.random_name()
        username = utils.random_username(first,last)
        email = utils.random_email(username)

        db_obj = Users(
                email=email,
                github_username=username,
                first_name=first,
                last_name=last
            )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    return db_obj

# def create_random_reviewers(random_reviewers: int,
#         db: Session):
    
    

    
