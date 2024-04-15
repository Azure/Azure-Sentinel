  # Google Cloud Platform Identity and Access Management Logic Apps Custom connector and playbook templates

  <img src="./GCP_IAMConnector/google_logo.svg" alt="drawing" width="20%"/><br>


## Table of Contents

1. [Overview](#overview)
1. [Custom Connector + 3 Playbook templates deployment](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)


<a name="overview">

# Overview

This custom connector connects to Google Cloud Platform (GCP) Identity and Access Management (IAM) API.

<a name="deployall">

## Custom Connector + 3 Playbook templates deployment
This package includes:
* [Logic Apps custom connector for GCP IAM](./GCP_IAMConnector)

* These three playbook templates leverage Proofpoint TAP custom connector:
  * [Enrichment – add information to incidents](./Playbooks/GCP-EnrichServiseAccountInfo) - Obtains additional information about GCP account and add it as a comment to the incident.
  * [Response - disable key](./Playbooks/GCP-DisableServiceAccountKey) - disables service account key in GCP.
  * [Response - disable service account](./Playbooks/GCP-DisableServiceAccountFromTeams) - posts adaptive card to Teams channel and disables service account after approving in Teams.

You can choose to deploy the whole package: connector + all three playbook templates, or each one seperately from it's specific folder.


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogleCloudPlatformIAM%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogleCloudPlatformIAM%2FPlaybooks%2Fazuredeploy.json)



# Google Cloud Platform IAM connector documentation 

<a name="authentication">

## Authentication
This connector supports OAuth2.0 authentication. Refer to the GoogleCloudPlatformIAM Custom Connector documentation for more details.

<a name="prerequisites">

### Prerequisites in GCP
To configure the connector follow the instructions:
1. Deploy the connector using **Deploy to Azure** button.
2. Enable Identity and Access Management (IAM) API in GCP Console (see [instructions](https://developers.google.com/identity/protocols/oauth2/web-server#enable-apis)).
3. Create authorization credentials (see [instructions](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)). As a redirection url, use the redirection url that you can find on the connector page (in Azure go to **Logic Apps Custom Connector** -> **GoogleCloudPlatformIAM** -> click **Edit** -> **Security** -> copy *Redirect URL*). If this is your first time creating a client ID, you can also configure your consent screen by clicking Consent Screen. (The [following procedure](https://support.google.com/cloud/answer/6158849?hl=en#userconsent) explains how to set up the Consent screen.) You won't be prompted to configure the consent screen after you do it the first time. Note that [the following scope](https://developers.google.com/identity/protocols/oauth2/scopes#iam) has to be enabled in the consent screen.
4. In Azure go to **Logic Apps Custom Connector** -> **GoogleCloudPlatformIAM** -> click **Edit** -> **Security** -> fill the *Client id* and *Client secret*, obtained in the previous step -> click **Update connector**.

<a name="deployment">

### Deployment instructions 
1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying custom connector and playbooks.

| Parameters | Description |
|----------------|--------------|
|**GCP-EnrichServiseAccountInfo Playbook Name** | Enter the playbook name here (e.g. GCP-EnrichServiseAccountInfo)|
|**GCP-DisableServiceAccountKey Playbook Name** | Enter the playbook name here (e.g. GCP-DisableServiceAccountKey)|
|**GCP-DisableServiceAccountFromTeams Playbook Name** | Enter the playbook name here (e.g. GCP-DisableServiceAccountFromTeams)|
|**TeamsGroupId** | Value of TeamsGroupId parameter in GCP-DisableServiceAccountFromTeams playbook. Id of the Teams Group where the adaptive card will be posted.|
|**TeamsChannelId** | Value of TeamsChannelId parameter in GCP-DisableServiceAccountFromTeams playbook. Id of the Teams Channel where the adaptive card will be posted.|

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Sentinel

Each Playbook requires a different type of configuration. Check documentation for each Playbook.


<a name="limitations">

## Known Issues and Limitations
