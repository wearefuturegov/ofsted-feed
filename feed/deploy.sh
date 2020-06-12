#!/usr/bin/env bash
set -euf -o pipefail

# This script should be called by ../deploy.sh unless you're all set up and configured and just need to redeploy this function.

# Account and GCP project
project_id=$(cat ../credentials/project.txt)
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")

# Ofsted function
# NB: outbound requests are routed through the VPC so they have a static IP address
token=$(cat ../credentials/token.txt)
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"
#wsdl="https://testinfogateway.ofsted.gov.uk/ISPPGateway/ISPPGatewayServices.svc?wsdl"
wsdl="./wsdl.xml"
gcloud functions deploy feed --runtime=nodejs10 --set-env-vars TOKEN=${token},PROJECT_NUMBER=${project_number},WSDL=${wsdl} ${options} \
    --vpc-connector ofsted-egress-vpcc \
    --egress-settings all

# Quick test...
echo "Breathe..."
sleep 2
curl -v https://europe-west2-${project_id}.cloudfunctions.net/feed?token=${token}
