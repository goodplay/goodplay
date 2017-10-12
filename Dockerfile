FROM docker:latest

MAINTAINER Benjamin Schwarze <benjamin.schwarze@mailboxd.de>

RUN apk add --no-cache \
    gcc \
    git \
    libffi-dev \
    make \
    musl-dev \
    openssl-dev \
    perl \
    py-pip \
    python \
    python-dev \
    sshpass \
    wget

RUN pip install 'ansible>=2.1,<2.2' goodplay
