#!/usr/bin/env bash
set -euf -o pipefail

# Account and GCP project
project_id=$(cat project.txt)
account=$(cat account.txt)

# Setup
gcloud config set account $account
gcloud config set project $project_id
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")

# Enable APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable vpcaccess.googleapis.com


# Egress through VPC to enable a static IP address
# See: https://cloud.google.com/functions/docs/networking/network-settings#route-egress-to-vpc

# IP
gcloud compute addresses describe ofsted-egress-ip --region=europe-west2 || \
gcloud compute addresses create ofsted-egress-ip --region=europe-west2

# Network
gcloud compute networks describe ofsted-egress-network || \
gcloud compute networks create ofsted-egress-network --subnet-mode=custom
#gcloud compute networks subnets describe ofsted-egress-subnet --region=europe-west2 || \
#gcloud compute networks subnets create ofsted-egress-subnet --network=ofsted-egress-network --range=10.0.0.0/29 --region=europe-west2

# Router
gcloud compute routers describe ofsted-egress-router --region=europe-west2 || \
gcloud compute routers create ofsted-egress-router \
    --network ofsted-egress-network \
    --region=europe-west2

# NAT
gcloud compute routers nats describe ofsted-egress-nat --router=ofsted-egress-router --region=europe-west2 || \
gcloud compute routers nats create ofsted-egress-nat \
    --router=ofsted-egress-router \
    --router-region=europe-west2 \
    --nat-primary-subnet-ip-ranges \
    --nat-external-ip-pool=ofsted-egress-ip

# VPC connector for function traffic egress
gcloud compute networks vpc-access connectors describe ofsted-egress-vpcc --region europe-west2 || \
gcloud compute networks vpc-access connectors create ofsted-egress-vpcc \
    --network=ofsted-egress-network \
    --region=europe-west2 \
    --range=10.0.0.16/28
gcloud projects add-iam-policy-binding $project_id \
    --member=serviceAccount:service-${project_number}@gcf-admin-robot.iam.gserviceaccount.com \
    --role=roles/viewer
gcloud projects add-iam-policy-binding $project_id \
    --member=serviceAccount:service-${project_number}@gcf-admin-robot.iam.gserviceaccount.com \
    --role=roles/compute.networkUser

# Ofsted certificate, key and key password
gcloud secrets describe public_key || \
gcloud secrets create public_key --data-file ../soap/examples/cert/pubkey.pem --replication-policy automatic
gcloud secrets describe private_key || \
gcloud secrets create private_key --data-file ../soap/examples/cert/privkey.pem --replication-policy automatic
gcloud projects add-iam-policy-binding $project_id \
    --member=serviceAccount:${project_id}@appspot.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor


# Ofsted function
# NB: outbound requests are routed through the VPC so they have a static IP address
token=$(cat token.txt)
options="--region=europe-west2 --memory=256MB --trigger-http --allow-unauthenticated"
gcloud functions deploy feed --runtime=nodejs10 --set-env-vars TOKEN=${token},PROJECT_NUMBER=${project_number} ${options} \
    --vpc-connector ofsted-egress-vpcc \
    --egress-settings all

# Quick test...
echo "Breathe..."
sleep 5
curl -v https://europe-west2-${project_id}.cloudfunctions.net/feed?token=${token}