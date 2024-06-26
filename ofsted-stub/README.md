# Ofsted stub

This application pretends to be ofsted, when you don't have a whitelisted IP yet.

```
docker build -t ofsted-stub .
docker run -p 3000:3000 --name ofsted-stub -d ofsted-stub
```

http://localhost:3000/
http://localhost:3000/api-docs/

Please note the schema is very loosely defined so any data validation may fail

## Deploy to google cloud

```sh
# build the image
cd ofsted-stub
project_id=$(gcloud config get-value project)
gcloud builds submit --tag gcr.io/${project_id}/ofsted-stub --timeout 15m


# deploy container
project_id=$(gcloud config get-value project)
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")
gcloud run deploy ofsted-stub --image=gcr.io/${project_id}/ofsted-stub \
  --platform=managed --region=europe-west1 --allow-unauthenticated


# check its status
gcloud run services list


# delete when done
gcloud run services delete ofsted-stub
```
