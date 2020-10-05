FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
# RUN pip install pipenv


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .