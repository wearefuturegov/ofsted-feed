FROM python:alpine

# Dependencies for building xmlsec and grpcio (from requirements.txt in the ofsted-client container image)
RUN apk update && apk add \
    gcc \
    g++ \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    xmlsec-dev \
    libffi-dev \
    openssl-dev

# Bump a build

RUN pip install xmlsec
RUN pip install grpcio
