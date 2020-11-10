FROM gcr.io/ofsted-feed/alpine-wheels

# Temporary until the next base image build
RUN apk update && apk add \
    libffi-dev \
    openssl-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app.py .
COPY tweaked_xml/ tweaked_xml/

ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app