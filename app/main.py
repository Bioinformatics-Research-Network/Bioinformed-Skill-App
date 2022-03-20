# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/

import fastapi
from app.api import services
from app.db.init_db import init

app = fastapi.FastAPI()

init()



