# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

ENV FLASK_ENV production

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "--capture-output", "--log-level", "debug", "--error-logfile", "-", "--access-logfile", "-", "--bind", ":8000", "wsgi:app"]
