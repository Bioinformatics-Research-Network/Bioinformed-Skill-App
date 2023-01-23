#!/bin/bash

smee -u $CRUD_SLACK_SMEE -p 2000 -P /api/reviewer/assign_reviewer_slack &
# Start the ghbot
gunicorn main:app --capture-output --log-level debug --error-logfile - \
--access-logfile - --bind :2000 --workers 2 \
--worker-class uvicorn.workers.UvicornWorker