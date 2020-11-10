#!/usr/bin/env bash
set -exuo pipefail

# docker build --tag ofsted-client .

parentdir=$(dirname "$PWD")
keyfile=${parentdir}/secrets/run-key.json
certfolder=${parentdir}/secrets/cert
messagefolder=${parentdir}/secrets/compare
project_id=$(gcloud config get-value project)
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")
function="https://europe-west2-${project_id}.cloudfunctions.net/proxy"

# docker run -it --rm -p 8080:8080 \
#   -v "${messagefolder}":/output \
#   -v "${keyfile}":/secrets/key \
#   --env GOOGLE_APPLICATION_CREDENTIALS="/secrets/key" \
#   --env PROJECT_NUMBER="${project_number}" \
#   --env FUNCTION_URL="${function}" \
#   --env FUNCTION_TOKEN=$(gcloud auth print-identity-token) \
#   --user $(id -u ${USER}):$(id -g ${USER}) \
#   ofsted-client

export GOOGLE_APPLICATION_CREDENTIALS=${keyfile}
export PROJECT_NUMBER=${project_number}
export FUNCTION_URL="${function}"
export FLASK_ENV=development
export FUNCTION_TOKEN=$(gcloud auth print-identity-token)

echo "Access token is $(cat ${parentdir}/secrets/token.txt)" 

flask run
