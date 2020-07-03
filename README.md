# Ofsted Feed Client
Client for the Ofsted feed.

## Setup

A few pointers for how this project is set up:

 * The feed runs servelessly in Google Cloud Platform using Cloud Functions and Cloud Run (container).
 * There's a bunch of network config here to route traffic out from Cloud Functions via a static IP so that the IP address can be whitelisted at Ofsted.

## Deployment

Deployment is done automatically from the Github repo whenever code is pushed using Github Actions and a GCP service sccount.

 * The deployment workflows are in [.github/workflows](.github/workflows)
 * Secrets, including the deployment service account key, are stored in [Github secrets](https://github.com/wearefuturegov/ofsted-feed/settings/secrets) in the settings area for this repo. The values can be updated, but can't be viewed.
 * NB the service accout key needs to be base-64 encoded as described in the [Setup-gcloud action documentation](https://github.com/GoogleCloudPlatform/github-actions/blob/master/setup-gcloud/README.md#inputs).

 In other words, the development workflow consists of editing and pushing code, followed by monitoring the deployment in this repo's [Actions tab](https://github.com/wearefuturegov/ofsted-feed/actions).

### Secrets

The deployment expects the following [Github secrets](https://github.com/wearefuturegov/ofsted-feed/settings/secrets).

Some example commands are provided in [secrets/cert/pfx-to-pem.txt](secrets/cert/pfx-to-pem.txt) to help with converting PFX-format Ofsted certificates to the PEM format that the Zeep soap library uses.

#### GOOGLE_APPLICATION_CREDENTIALS

A base-64 encoded representation of a json-format GCP service account key. The service account is used for deployment so will need elevated permissions (NB the account can be disabled when not in use fon added safety).

Once you have created a service account, generated a key and downloaded the json file, the secret value can be generated as follows:

    cat myproject-7fdd5b1966dc.json | base64 > deploy-key.txt

The contents of `deploy-key.txt` can then be copied and pasted into the secret value.

See also the [Setup-gcloud action documentation](https://github.com/GoogleCloudPlatform/github-actions/blob/master/setup-gcloud/README.md#inputs).

#### PROJECT_ID

The GCP project ID that you are deploying to. This is a string value such as `myproject-123456`

#### OFTSED_USERNAME

The username provided to you by Ofsted

#### OFTSED_PASSWORD

The password provided to you by Ofsted

#### OFTSED_CERTIFICATE

The certificate, in pem format, provided to you by Ofsted, e.g.: 

    Bag Attributes
        localKeyID: 00 00 00 00 
    subject=DC = uk, DC = gov, DC = ofsted, DC = ofsteded, OU = Extranet User Accounts, OU = ISPP, CN = xxxx

    issuer=DC = uk, DC = gov, DC = ofsted, DC = ofsteded, CN = Ofsted KSP1 Issuing CA

    -----BEGIN CERTIFICATE-----
    ...base64...
    ...base64...
    ...base64...
    -----END CERTIFICATE-----

#### OFTSED_PRIVATE_KEY

The private key, in pem format, of the certificate provided to you by Ofsted, e.g.: 

    -----BEGIN RSA PRIVATE KEY-----
    ...base64...
    ...base64...
    ...base64...
    -----END RSA PRIVATE KEY-----

## Notes

Both a Cloud Run container and a Cloud Function are used:

 * The cloud functions Python runtime does not contain the `libxmlsec1` system package so it's not possible to sign soap messages in GCF using Python (https://issuetracker.google.com/issues/158846273)
 * For this reason a Cloud Run container is used to generate the soap xml and this is then passed to a function, which acts as an egress proxy to send the message to Ofsted via the static IP.
 