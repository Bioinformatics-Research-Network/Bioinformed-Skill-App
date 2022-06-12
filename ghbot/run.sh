#!/bin/bash

# Start the smee client
smee -u https://smee.io/rSiwWHyU4AMt1zn --port 2000 &

# Start the ghbot
gunicorn main:app --capture-output --log-level debug --error-logfile - \
--access-logfile - --bind :2000 --workers 2 \
--worker-class uvicorn.workers.UvicornWorker
