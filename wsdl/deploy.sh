#!/usr/bin/env bash
set -euf -o pipefail

# Account and GCP project
project_id=$(cat project.txt)
account=$(cat account.txt)

# Setup
gcloud config set account $account
gcloud config set project $project_id

# Enable APIs
gcloud services enable cloudfunctions.googleapis.com

# Ofsted wsdl function
# NB: outbound requests are routed through the VPC so they have a static IP address
token=$(cat token.txt)
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"
gcloud functions deploy wsdl --runtime=nodejs10 --set-env-vars TOKEN=${token} ${options} \
    --vpc-connector ofsted-egress-vpcc \
    --egress-settings all

# Quick test...
echo "Breathe..."
sleep 2
curl -v https://europe-west2-${project_id}.cloudfunctions.net/wsdl?token=${token}
