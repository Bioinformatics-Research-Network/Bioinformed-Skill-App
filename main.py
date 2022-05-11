# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.initiate_db import init_db, init_db_real
from app.db.fill_db import create_database
from app.api.services import get_db
from app.api import api_endpoints


app = FastAPI()

# initialize database, creates new database if it doesn't exist. It doesn't add fake data.
# For fake data entry see: app\db\create_fake_data.py
init_db_real()
create_database()


@app.get("/")
def root(db: Session = Depends(get_db)):
    """
    Root api endpoint, has no specific function. Was created to test API.

    :param db: Generator for Session of database

    :returns: json with "Hello World!"
    """
    return {"Hello World!"}


# Router links all the api endpoints to main.py
app.include_router(api_endpoints.router)
