import app.db.models as models


def verify_check(assessment_tracker_entry: models.AssessmentTracker):
    """
    Verifies that the commit is passing the checks.

    :param db: Generator for Session of database
    :param assessment_tracker_entry: inputs assessment tracker entry from database

    :returns: boolean True if the latest commit is passing the checks.

    :errors: ValueError if logs are not available or if the commit has not been checked.
    """
    # Get the log
    log = assessment_tracker_entry.log
    if log is None:
        raise ValueError("No logs found.")

    # Get latest commit
    last_log_by_commit = [
        lg
        for lg in log
        if lg.get("commit", "NA") == assessment_tracker_entry.latest_commit
    ]
    if last_log_by_commit == []:
        raise ValueError("No logs found for latest commit.")

    # Get the logs where checks were run
    commit_log_checks = [
        lg for lg in last_log_by_commit if "checks_passed" in lg.keys()
    ]
    if commit_log_checks == []:
        raise ValueError("Check results not available for latest commit.")
    last_log = commit_log_checks[-1]
    # Return checks results
    return last_log["checks_passed"]
