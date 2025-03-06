FROM python:3.8

ADD requirements.txt /app/requirements.txt
WORKDIR /app


RUN apt install libpq-dev -y
RUN pip install -r requirements.txt