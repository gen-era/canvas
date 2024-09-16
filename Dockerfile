FROM python:3.12.6-alpine

RUN apk update && apk add --no-cache gcc musl-dev postgresql-dev

# set work directory
WORKDIR /usr/src/canvas

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .