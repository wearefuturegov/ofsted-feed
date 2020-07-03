#!/usr/bin/env bash
set -euf -o pipefail

project_id=$(gcloud config get-value project)
token=$(cat ../secrets/token.txt)

url=https://europe-west2-${project_id}.cloudfunctions.net/wsdl?token=${token}

echo Calling: $url
curl -v $url
