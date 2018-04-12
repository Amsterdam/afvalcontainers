FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

COPY . /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

USER datapunt
