# syntax=docker/dockerfile:1

FROM public.ecr.aws/lambda/python:3.9

RUN yum install -y unzip

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . .

CMD ["handler.lambda_handler"]
