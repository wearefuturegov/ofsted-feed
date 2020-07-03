FROM gcr.io/ofsted-feed/alpine-wheels

# Dependencies for building xmlsec (specified in requirements.txt)
RUN apk update && apk add \
    gcc \
    g++ \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    xmlsec-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY src/ .


USER 1000
ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app