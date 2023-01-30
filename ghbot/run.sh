#!/bin/bash

smee -u $GHBOT_SMEE --port 2000 &
# Start the ghbot
gunicorn main:app --capture-output --log-level debug --error-logfile - \
--access-logfile - --bind :2000 --workers 2 \
--worker-class uvicorn.workers.UvicornWorker
