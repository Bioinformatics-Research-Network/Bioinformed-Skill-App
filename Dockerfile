# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

ENV FLASK_ENV production

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["gunicorn", "--capture-output", "--log-level", "debug", "--error-logfile", "-", "--access-logfile", "-", "--bind", ":8000", "wsgi:app"]
