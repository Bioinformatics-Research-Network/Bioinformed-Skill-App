# to create random data and test other crud utils
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate
from app import models
from app.utils import utils

def create_random_user(int): # imput number of random users to create
    first, last = utils.random_name()
    username = utils.random_username(first,last)
    email = utils.random_rmail(username)
    