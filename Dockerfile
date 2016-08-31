FROM docker:latest

MAINTAINER Benjamin Schwarze <benjamin.schwarze@mailboxd.de>

RUN apk add --no-cache \
    ansible \
    git \
    py-pip

RUN pip install goodplay
