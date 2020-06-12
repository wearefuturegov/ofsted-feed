#!/usr/bin/env bash
set -euf -o pipefail

project_id=$(cat project.txt)
token=$(cat token.txt)

url=https://europe-west2-${project_id}.cloudfunctions.net/feed?token=${token}

echo Calling: $url
curl -v $url
