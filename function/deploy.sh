#!/usr/bin/env bash
set -euf -o pipefail

# Account and GCP project
project_id=$(cat project.txt)
account=$(cat account.txt)
token=$(cat token.txt)

# Setup
gcloud config set account $account
gcloud config set project $project_id

# Ofsted function
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"
gcloud functions deploy feed --runtime=nodejs10 --set-env-vars TOKEN=${token} ${options}
