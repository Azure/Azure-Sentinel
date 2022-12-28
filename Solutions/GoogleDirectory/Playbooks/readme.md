# Tenable Logic Apps connector and playbook templates

<img src="./GoogleDirectoryAPIConnector/google_logo.svg" alt="drawing" width="20%"/><br>

## Table of Contents

1. [Overview](#overview)
1. [Custom Connector + 3 Playbook templates deployment](#deployall)
1. [Authentication](#authentication)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post-Deployment Steps](#postdeployment)

<a name="overview">

# Overview

This custom connector connects to [Google Directory Users API](https://developers.google.com/admin-sdk/directory/reference/rest/v1/users).

<a name="deployall">

## Custom Connector + 3 Playbook templates deployment

This package includes:

* [Logic Apps custom connector for Google Directory API](./GoogleDirectoryAPIConnector/)


* These three playbook templates leverage Tenable custom connectors:
  * [Google-EnrichIncidentWithUserInfo](./Playbooks/Google-EnrichIncidentWithUserInfo/)
  * [Google-SignOutUser](./Playbooks/Google-SignOutUser/)
  * [Google-SuspendUser](./Playbooks/Google-SuspendUser/)

You can choose to deploy the whole package: connector + all three playbook templates, or each one seperately from its specific folder.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogleDirectory%2FPlaybooks%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogleDirectory%2FPlaybooks%2Fazuredeploy.json)

# Tenable connectors documentation 

<a name="authentication">

## Authentication

*  OAuth2.0 authentication

<a name="prerequisites">

### Prerequisites

To configure the connector follow the instructions:
1. Deploy the connector using **Deploy to Azure** button.
2. Create authorization credentials (see [instructions](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)). As a redirection url, use the redirection url that you can find on the connector page (in Azure go to **Logic Apps Custom Connector** -> **GoogleDirectory** -> click **Edit** -> **Security** -> copy *Redirect URL*). If this is your first time creating a client ID, you can also configure your consent screen by clicking Consent Screen. (The [following procedure](https://support.google.com/cloud/answer/6158849?hl=en#userconsent) explains how to set up the Consent screen.) You won't be prompted to configure the consent screen after you do it the first time. Note that the scope `https://www.googleapis.com/auth/admin.directory.user` has to be enabled in the consent screen.
3. In Azure go to **Logic Apps Custom Connector** -> **GoogleDirectory** -> click **Edit** -> **Security** -> fill the *Client id* and *Client secret*, obtained in the previous step -> click **Update connector**.

<a name="deployment">

### Deployment instructions 

1. To deploy Custom Connectors and Playbooks, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters for deploying Custom Connectors and Playbooks

| Parameters | Description |
|----------------|--------------|
|**GoogleDirectoryConnectorName** | Logic App Connector Name |
|**Google-SuspendUser** | Name of the Playbook |
|**Google-SignOutUser** | Name of the Playbook |
|**Google-EnrichIncidentWithUserInfo** | Name of the Playbook |
|**TeamsGroupId** | Value of TeamsGroupId parameter in Google-SuspendUser playbook. Id of the Teams Group where the adaptive card will be posted.|
|**TeamsChannelId** | Value of TeamsChannelId parameter in Google-SuspendUser playbook. Id of the Teams Channel where the adaptive card will be posted.|

<br>
<a name="postdeployment">

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection. Check documentation for each Playbook.

#### b. Configurations in Sentinel

1. In Microsoft sentinel, analytical rules should be configured to trigger an incident that contains Accounts. In the *Entity maping* section of the analytics rule creation workflow, user email should be mapped to **FullName** identitfier of the **Account** entity type. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook. Check the [documentation](https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook) to learn more about automation rules.
