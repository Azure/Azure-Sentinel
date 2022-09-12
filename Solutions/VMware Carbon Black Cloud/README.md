# VMware Carbon Black Cloud Solution

![Carbon Black logo](./Data%20Connectors/CarbonBlack.PNG)

> **Important**
>
> The playbooks, workbook, and analytic rules included in `\Solutions\CarbonBlack` should be deployed from the [Microsoft Sentinel content hub]('https://docs.microsoft.com/azure/sentinel/sentinel-solutions-deploy#install-or-update-a-solution') rather than being deployed using the documentation below.
>
> This solution requires the [VMware Carbon Black Endpoint Standard Sentinel data connector]('https://docs.microsoft.com/azure/sentinel/data-connectors-reference#vmware-carbon-black-endpoint-standard-preview') from the Data Connector gallery.
>

## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)

## Overview

The Carbon Black Cloud is a cloud-native endpoint protection platform (EPP) that provides what you need to secure your endpoints using a single, lightweight agent and an easy-to-use console.

<a name="deployall">

## Manually deploy playbook templates and connector

This package includes:

* [Logic Apps custom connector for Carbon Black](./Data%20Connectors)

  ![custom connector](./Data%20Connectors/CarbonBlackListOfActions.png)

* Three playbook templates:

  * [Response from Teams](./Playbooks/CarbonBlack-TakeDeviceActionFromTeams) - allow SOC to take action on suspicious devices arrived in incidents (apply a pre-defined policy or quarantine) and change incident configuration directly from Teams channel. Post information about the incident as a comment to the incident.
  * [Quarantine device](./Playbooks/CarbonBlack-QuarantineDevice) - move the device arrived in the incident to quarantine (if not already quarantined). Post information about the incident as a comment to the incident.
  * [Enrichment](./Playbooks/CarbonBlack-DeviceEnrichment) - collect information about the devices and post them as incident comment.

You can choose to deploy the whole package (Connector and all three playbook templates), or each one seperately from each folder.

  [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCarbonBlack%2Fazuredeploy.json)

## Carbon Black Logic Apps custom connector

<a name="authentication">

## Authentication

This connector supports API Key authentication. When creating the connection for the custom connector, you must provide the API Secret and API key which you generated in Carbon Black Cloud console. [API Key authentication](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key).

> *Note*
> The API Key must be provided as a combination {API Key}/{API ID}.

<a name="prerequisites">

### Carbon Black Cloud prerequisites

1. Know your Carbon Black Cloud API service endpoint. [Determine your Carbon Black Cloud API service endpoint.](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#building-your-base-urls) (e.g. https://defense.conferdeploy.net)
2. Know your Carbon Black Org Key [Where is the Carbon Black Org Key found?](https://community.carbonblack.com/t5/Knowledge-Base/Carbon-Black-Cloud-Where-is-the-Org-Key-Found/ta-p/80970)
3. Create a custom Access level with the following minimum access:

   * Device > General Information > “device” allow permissions for “READ”
   * Device > Policy assignment > “device.policy” allow permissions for “UPDATE”
   * Device > Quarantine > “device.quarantine” allow permissions for “EXECUTE”
   * Search > Events > “org.search.events”, allow permission to CREATE to start a job, READ to get results, DELETE to cancel a search and UPDATE for watchlist actions.
   * Alerts > General Information > “org.alerts” allow permissions for “READ”
   * Alerts > Dismiss > “org.alerts.dismiss” allow permissions for “EXECUTE”
   * Alerts > Notes > “org.alerts.notes” allow permissions for “CREATE”, “READ”, and “DELETE”
  
4. Create an API key and secret using the Access Level type "Custom", and the Access Level you created. [How to generate a Carbon Black Cloud API Key](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#creating-an-api-key)
5. (Optional) Create a Carbon Black device policy for which to move devices, when requested from the Microsoft Teams playbook.

<a name="deployment">

### Deployment instructions

1. Deploy the custom connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

#### Custom connector parameters

| Parameters | Description |
|----------------|--------------|
|**Custom Connector name**| Custom connector name (e.g. CarbonBlackConnector) |
|**Service Endpoint** | Carbon Black Cloud API endpoint [Determine your Carbon Black Cloud API service endpoint.](https://developer.carbonblack.com/reference/carbon-black-cloud/authentication/#building-your-base-urls) |

#### Playbook parameters

| Parameters | Description |
|----------------|--------------|
|**CarbonBlack-TakeDeviceActionFromTeams Playbook Name**| Playbook name (e.g. CarbonBlack-TakeDeviceActionFromTeams) |
|**CarbonBlack-DeviceEnrichment Playbook Name** | Playbook name (e.g. CarbonBlack-QuarantineDevice) |
|**CarbonBlack-QuarantineDevice Playbook Name** | Playbook name (e.g. CarbonBlack-DeviceEnrichment) |
|**Org Key** | Carbon Black Cloud Org Key [Where is the Carbon Black Org Key found?](https://community.carbonblack.com/t5/Knowledge-Base/Carbon-Black-Cloud-Where-is-the-Org-Key-Found/ta-p/80970) |
|**Policy Id** | Carbon Black Policy Id to which the Microsoft Teams adaptive card will offer to move device |
|**Teams GroupId** | Microsoft Teams group to send the adaptive card [How to determine the Microsoft Teams channel and group ids](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps) |
|**Teams ChannelId** | Microsoft Teams channel to send the adaptive card [How to determine the Microsoft Teams channel and group ids](https://docs.microsoft.com/powershell/module/teams/get-teamchannel?view=teams-ps) |

<a name="postdeployment">

### Post-Deployment instructions

#### Authorize connections

Once the playbook is deployed, edit the Logic App and authorize each Carbon Black Cloud and Microsoft Teams connection.

1. Click the connection resource
2. Click edit or create new API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections such as the Microsoft Teams connection and Carbon Black connector connection.

> *Note*
> The API Key must be provided as a combination {API Key}/{API ID}.

#### Sentinel configurations

1. Microsoft Sentinel analytics rules should be configured to trigger an incident with risky user account.
2. Configure the automation rules to trigger the playbooks.

<a name="limitations">

## Known Issues and Limitations

1. Quarantine is not supported for Linux OS devices.
