# ofsted-feed
Interface to the Ofsted feed.

## Setup

A few pointers for how this project is set up:

 * The feed runs servelessly in Google Cloud Platform using Cloud Functions and Cloud Run (container).
 * There's a bunch of network config here to route traffic out from Cloud Functions via a static IP so that the IP address can be whitelisted at Ofsted.

## Deployment

Deployment is done automatically from the Github repo whenever code is pushed using Github Actions and a GCP service sccount.

 * The deployment workflows are in [.github/workflows](.github/workflows)
 * Secrets, including the deployment service account key, are stored in [Github secrets](https://github.com/wearefuturegov/ofsted-feed/settings/secrets) in the settings area for this repo. The values can be updated, but can't be viewed.
 * NB the service accout key needs to be base-64 encoded as described in the [Actions GCP documentation](https://github.com/marketplace/actions/google-cloud-platform-gcp-cli-gcloud#secrets).

 In other words, the development workflow consists of editing and pushing code, followed by monitoring the deployment in this repo's [Actions tab](https://github.com/wearefuturegov/ofsted-feed/actions).

## Notes

 * The cloud functions Python runtime does not contain the `libxmlsec1` system package so it's not possible to sign soap messages in GCF using Python (https://issuetracker.google.com/issues/158846273). For this reason a Cloud Run container is used to generate the xml and a function is then used to send the message to Ofsted via the static IP.
 