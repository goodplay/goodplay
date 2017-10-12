FROM docker:latest

MAINTAINER Benjamin Schwarze <benjamin.schwarze@mailboxd.de>

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.5/main' >> /etc/apk/repositories && apk add --no-cache \
    ansible==2.2.1.0-r0 \
    git \
    py-pip \
    wget

RUN pip install goodplay
