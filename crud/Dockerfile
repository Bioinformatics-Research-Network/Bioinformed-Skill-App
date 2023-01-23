# syntax=docker/dockerfile:1

FROM python:3.10

ARG CRUD_SLACK_SMEE

ENV CRUD_SLACK_SMEE ${CRUD_SLACK_SMEE}

RUN curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh && \
bash /tmp/nodesource_setup.sh && \
apt install nodejs -y && \
npm install -g smee-client

ENV APP_ENV production

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 2000

CMD ./smee_run.sh