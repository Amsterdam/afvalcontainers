FROM ubuntu:20.04
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN apt-get update && apt-get upgrade -y
RUN mkdir -p /static && chown datapunt /static

COPY src /app/
COPY deploy /deploy/
COPY requirements.txt /app/

WORKDIR /app


RUN pip install --no-cache-dir -r requirements.txt

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=containers.settings

RUN python manage.py collectstatic --no-input

CMD uwsgi

