#!/usr/bin/env bash
set -euf -o pipefail

project_id=$(cat ../credentials/project.txt)
token=$(cat ../credentials/token.txt)

url=https://europe-west2-${project_id}.cloudfunctions.net/wsdl?token=${token}

echo Calling: $url
curl -v $url
