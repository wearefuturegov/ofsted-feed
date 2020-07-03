#!/usr/bin/env bash
set -euf -o pipefail

project_id=$(gcloud config get-value project)
token=$(cat ../credentials/token.txt)

# url=https://europe-west2-${project_id}.cloudfunctions.net/feed?token=${token}
url=https://europe-west2-${project_id}.cloudfunctions.net/proxy?token=test

echo Calling: $url
#curl -v $url

curl -X post -d @"../secrets/example-messages/Fiddler SOAP Request - FIDY.xml" -H "content-type: text/xml" $url