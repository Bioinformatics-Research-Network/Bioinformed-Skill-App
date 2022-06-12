# syntax=docker/dockerfile:1

# Set up the app
FROM python:3.10-slim-buster
ENV APP_ENV production
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
EXPOSE 1234
CMD ["gunicorn", "main:app", "--capture-output", "--log-level", "debug", "--error-logfile", "-", "--access-logfile", "-", "--bind", ":1234", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]
