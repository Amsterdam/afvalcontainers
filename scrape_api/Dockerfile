FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

EXPOSE 8000

# only do a pip install if requirements are changed
COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY . /app/

WORKDIR /app
