#!/usr/bin/env bash
set -euf -o pipefail

# This script should be called by ../deploy.sh unless you're all set up and configured and just need to redeploy this function.

# Account and GCP project
project_id=$(gcloud config get-value project)

# Ofsted wsdl function
# NB: outbound requests are routed through the VPC so they have a static IP address
token=$(cat ../secrets/token.txt)
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"
gcloud functions deploy wsdl --runtime=nodejs10 --set-env-vars TOKEN=${token} ${options} \
    --vpc-connector ofsted-egress-vpcc \
    --egress-settings all

# Quick test...
echo "Breathe..."
sleep 2
curl -v https://europe-west2-${project_id}.cloudfunctions.net/wsdl?token=${token}
