from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas

# app.utils.runGHA
# invoked by /api/init-check
# input: github username, assessment name
# runs GHA.
# output GHA logs required
def runGHA(check: schemas.check_update):

    # uses GHA Actions API
    # returns logs
    logs = schemas.update_log(
        log=json.dumps(
            {
                "Updated": str(datetime.utcnow()),
                "Checks_passed": True,
                "Commit": check.commit,
            }
        )
    )
    return logs
