FROM python:3.7-bookworm
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y \
	gdal-bin \
	libpcre3 libpcre3-dev \
        netcat-traditional \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static \
	&& pip install uwsgi

# Setup certificates for ADP/Motiv
RUN apk add ca-certificates
COPY adp_rootca.crt /usr/local/share/ca-certificates/adp_rootca.crt
RUN chmod 644 /usr/local/share/ca-certificates/adp_rootca.crt && update-ca-certificates –fresh

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

USER datapunt

COPY src /app/
COPY deploy /deploy/

RUN export DJANGO_SETTINGS_MODULE=containers.settings

RUN python manage.py collectstatic --no-input

CMD uwsgi

