FROM atpipeline/atcore:dev

RUN apt-get -y install --no-install-recommends python3 python3-venv python3-pip

WORKDIR /app
COPY ./requirements.txt .
RUN /usr/bin/python3 -m venv ENV && \
    ENV/bin/pip install --no-cache-dir wheel && \
    ENV/bin/pip install --no-cache-dir -r requirements.txt

ADD . /app

EXPOSE 5050

ENTRYPOINT ["/app/entry-point.sh"]
CMD ["/app/ENV/bin/python3", "main.py"]
