FROM python:alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY src/ .

ENV PORT 8080

USER 1000
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app