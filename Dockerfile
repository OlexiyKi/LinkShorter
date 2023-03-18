# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .



#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       (git token)