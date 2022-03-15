# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

import fastapi
from app.api import services

app = fastapi.FastAPI()

services.create_database()
# initiializing database


