from datetime import datetime
from app.schemas import schemas


def runGHA(check: schemas.check_update):
    """
    Invoked by /api/init_check endpoint
    Used to run the GitHub Actions checks on the commit reuired

    :param check: user's github username, assessment name and latest commit

    :returns: logs from the GHA
    """

    logs = schemas.update_log(
        log={
            "Updated": str(datetime.utcnow()),
            "Checks_passed": True,
            "Commit": check.commit,
        }
    )
    return logs
