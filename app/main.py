# FastAPI should be called here
# Global Security should go here -- see https://fastapi.tiangolo.com/tutorial/security/first-steps/


import fastapi
from app.tests.utils import utils
app = fastapi.FastAPI()

# initiializing database
utils.create_database()


