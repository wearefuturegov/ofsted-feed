# Ofsted Feed Client

Client for the [Ofsted feed](https://docs.google.com/drawings/d/1H2PbfclwaD_IyS6-6kGQPtuJ2xxGeuLtD_rHhqxdkEY). This project connects to the new ofsted endpoint, the one that returns json.

## Setup

A few pointers for how this project is set up:

- The feed runs servelessly in Google Cloud Platform using Cloud Functions and Cloud Run (container).
- There's a bunch of network config here to route traffic out from Cloud Functions via a static IP so that the IP address can be whitelisted at Ofsted.

**Setup google cloud**:

- You will need a google cloud account with billing enabled.
- Go to IAM and admin and create a new service account called `deploy` use the description `Github actions deployment account`
- Grant `Owner` permissions

You can also do it via the gcloud cli if you have it configured:

```sh
# create service account
gcloud iam service-accounts create deploy --description="Github actions deployment account" --display-name="deploy"

# copy the 'email' field for  your new service account
gcloud iam service-accounts list

project_id=$(gcloud config get-value project)

# set service account permissions
gcloud projects add-iam-policy-binding ${project_id} \
    --member=serviceAccount:<EMAILHERE> \
    --role=roles/owner

# check its worked
gcloud projects get-iam-policy ${project_id}  \
--flatten="bindings[].members" \
--format='table(bindings.role)' \
--filter="bindings.members:<EMAILHERE>"


# download IAM keys for GOOGLE_APPLICATION_CREDENTIALS
gcloud iam service-accounts keys create ./${project_id}-service-account-keys.json --iam-account <EMAILHERE>

cat ./${project_id}-service-account-keys.json | base64 > deploy-key.txt
```

**Setup github repo**:

Go to settings > Secrets and variables > Actions

See [secrets](#secrets) section below for more information

You will need to have the following secrets in your repo:

- `PROJECT_ID`
- `OFSTED_API_KEY`
- `OFSTED_SERVICE_KEY`
- `OFSTED_LOCAL_AUTHORITY_CODE`
- `ACCESS_TOKEN`
- `GOOGLE_APPLICATION_CREDENTIALS` will be the output of deploy-key.txt above

## Deployment

Deployment is done automatically from the Github repo whenever code is pushed using Github Actions and a GCP service sccount.

- The deployment workflows are in [.github/workflows](.github/workflows)
- Secrets, including the deployment service account key, are stored in [Github secrets](https://github.com/wearefuturegov/ofsted-feed/settings/secrets) in the settings area for this repo. **The values can be updated, but can't be viewed.**
- NB the service accout key needs to be base-64 encoded as described in the [Setup-gcloud action documentation](https://github.com/GoogleCloudPlatform/github-actions/blob/master/setup-gcloud/README.md#inputs).

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

#### OFSTED_API_KEY

The api_key provided to you by Ofsted

#### OFSTED_SERVICE_KEY

The service_key provided to you by Ofsted

#### OFSTED_LOCAL_AUTHORITY_CODE

The service_key provided to you by Ofsted

#### ACCESS_TOKEN

Token passed though by Outpost to ensure correct authentication

`node secrets/generate_token.js && cat secrets/token.txt`

## gcloud CLI

This project works by running gcloud commands through github actions to setup and deploy the application. You can do the same actions locally on your machine using [gcloud CLI](https://cloud.google.com/sdk/gcloud)

```sh
# list your configurations
gcloud config configurations list

# list enabled services
gcloud services list --enabled
```
