FROM python:3.7-buster as builder
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    python3-pip \
    python3-dev \
    libpq-dev

#RUN apt-get install python3-pip -y
RUN adduser --system datapunt
RUN mkdir -p /static && chown datapunt /static

COPY src /app/
COPY deploy /deploy/

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=containers.settings

RUN python manage.py collectstatic --no-input

CMD uwsgi

