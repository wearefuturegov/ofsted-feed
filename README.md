# ofsted-feed
Interface to the Ofsted feed.

## Setup

A few pointers for how this project is set up:

 * The feed runs servelessly in Google Cloud Platform using Cloud Functions and Cloud Run (container).
 * There's a bunch of network config here to route traffic out from Cloud Functions via a static IP so that the IP address can be whitelisted at Ofsted.

## Deployment

Deployment is done direct from the Github repo using Github Actions and a GCP service sccount.

 * The deployment workflows are in [.github/workflows](https://github.com/wearefuturegov/ofsted-feed/tree/master/.github/workflows) [relative](tree/master/.github/workflows)
 * Secrets, including the deployment service account key, are stored in [Github secrets](https://github.com/wearefuturegov/ofsted-feed/settings/secrets) [relative](settings/secrets)

## Notes

 * The cloud functions Python runtime is missing the `libxmlsec1` system package so it's not possible to sign soap messages in Python (https://issuetracker.google.com/issues/158846273). For this reason a container is used to generate the xml and a function is used to send the message out via the static IP.