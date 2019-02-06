FROM python:3.7
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ADD . /app
WORKDIR /app
EXPOSE 5050

ENTRYPOINT ["/app/entry-point.sh"]
CMD ["python3", "main.py"]