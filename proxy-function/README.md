# Proxy function

This app runs as a function and relays the ofsted feed data to our ofsted-client application. The IP address of its VPC is the one whitelisted by ofsted.

```
docker build -t proxy-function .
docker run -p 3001:8080 --name proxy-function -e ENDPOINT_SERVICE=http://host.docker.internal:3000 -d proxy-function
```

## Deploy to google cloud

```sh
# deploy it
project_id=$(gcloud config get-value project)
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")
ofsted_stub=$(gcloud run services describe ofsted-stub --platform=managed --region=europe-west1 --format="value(status.url)")
gcloud functions deploy ofsted_feed_proxy \
--runtime=python312 --region=europe-west2 --memory=256MB --trigger-http \
--no-allow-unauthenticated \
--vpc-connector ofsted-egress-vpcc \
--egress-settings all \
--timeout=540 \
--service-account=${project_number}-compute@developer.gserviceaccount.com \
--set-env-vars ENDPOINT_SERVICE=${ofsted_stub},PROJECT_ID=${project_id}


# allow it to be accessed internally

gcloud functions add-iam-policy-binding ofsted_feed_proxy --region europe-west2 \
--member=serviceAccount:${project_number}-compute@developer.gserviceaccount.com \
--role=roles/cloudfunctions.invoker
```
