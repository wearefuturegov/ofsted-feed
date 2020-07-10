#!/usr/bin/env bash
set -exuo pipefail

docker build --tag ofsted-client .

parentdir=$(dirname "$PWD")
keyfile=${parentdir}/secrets/run-key.json
certfolder=${parentdir}/secrets/cert
project_id=$(gcloud config get-value project)
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")
function="https://europe-west2-${project_id}.cloudfunctions.net/proxy"

docker run -it --rm -p 8080:8080 \
  -v "${keyfile}":/secrets/key \
  --env GOOGLE_APPLICATION_CREDENTIALS="/secrets/key" \
  --env PROJECT_NUMBER="${project_number}" \
  --env FUNCTION="${function}" \
  ofsted-client

