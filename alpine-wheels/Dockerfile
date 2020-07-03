FROM python:alpine

# Dependencies for building xmlsec (specified in requirements.txt)
RUN apk update && apk add \
    gcc \
    g++ \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    xmlsec-dev

RUN pip install xmlsec
RUN pip install grpcio
