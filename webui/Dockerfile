# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

ENV APP_ENV production

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 8000

# CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]
# Modified gunicorn command from https://pythonspeed.com/articles/gunicorn-in-docker/
# Needed to avoid hanging error: https://github.com/benoitc/gunicorn/issues/1952
CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--capture-output", "--log-level", "debug", "--error-logfile", "-", "--access-logfile", "-", "--bind", ":8000", "wsgi:app"]
