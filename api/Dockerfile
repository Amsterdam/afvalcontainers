FROM ubuntu:20.04
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN set -xe
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-pip
RUN adduser --system datapunt
RUN mkdir -p /static && chown datapunt /static

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/
COPY deploy /deploy/
COPY requirements.txt /app/

WORKDIR /app

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=containers.settings

RUN python manage.py collectstatic --no-input

CMD uwsgi

