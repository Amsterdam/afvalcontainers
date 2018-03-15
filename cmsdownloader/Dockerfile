FROM amsterdam/python

RUN adduser --system datapunt
RUN rm -rf /tmp
RUN mkdir -p /tmp
RUN chown datapunt /tmp

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

USER datapunt

CMD /app/docker-run.sh