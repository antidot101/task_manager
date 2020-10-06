FROM python:3.7.3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /ptm
WORKDIR /ptm

COPY requirements.txt /ptm/
RUN pip install -r requirements.txt

EXPOSE 8080

COPY . /ptm/