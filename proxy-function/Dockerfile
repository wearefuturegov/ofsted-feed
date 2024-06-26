FROM python:3.12-slim
ARG ENDPOINT_SERVICE
ENV ENDPOINT_SERVICE=$ENDPOINT_SERVICE

WORKDIR /app
COPY main.py main.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Run the web service on container startup.
CMD exec functions-framework --target=ofsted_feed_proxy --debug

