# Ofsted client

This app returns the ofsted feed data to Outpost through the proxy-function.

## Deploy to google cloud

```sh
project_id=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${project_id}/ofsted-feed-client --timeout 15m


project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")
function_url=https://europe-west2-${project_id}.cloudfunctions.net/ofstead_feed_proxy
gcloud run deploy ofsted-feed-client --image=gcr.io/${project_id}/ofsted-feed-client \
--platform=managed --region=europe-west1 --allow-unauthenticated \
--update-env-vars=FUNCTION_URL=${function_url},PROJECT_ID=${project_id}
```
