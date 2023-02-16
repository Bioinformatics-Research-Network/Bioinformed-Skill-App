# syntax=docker/dockerfile:1

# Set up the app
FROM python:3.10

ARG GHBOT_SMEE

ENV GHBOT_SMEE ${GHBOT_SMEE}

# Get the smee client for proxying webhook payloads
RUN curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh && \
bash /tmp/nodesource_setup.sh && \
apt install nodejs -y && \
npm install -g smee-client

# Set up the app and run it
ENV APP_ENV production
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
EXPOSE 2000
CMD ./run.sh
