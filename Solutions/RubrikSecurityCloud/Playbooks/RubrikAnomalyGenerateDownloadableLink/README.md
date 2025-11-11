# Rubrik Anomaly Generate Downloadable Link

## Summary

This playbook will generate downloadable links according to objectType (VMware, Fileset or VolumeGroup) and add suspiciousFiles and downloadable links as an incident comment to enrich the anomaly.

### Prerequisites

1. The Rubrik Security Cloud data connector should be configured to send appropriate events to Microsoft Sentinel.
2. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to perform the desired operations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
3. Obtain Teams GroupId and ChannelId
    * Create a Team with public channel.
    * Click on three dots (...) present on right side of the your newly created teams channel and Get link to the channel.
    * Copy the text from the link between /channel and /, decode it using online url decoder and copy it to use as channelId.
    * Copy the text of groupId parameter from link to use as groupId.
4. Make sure that RubrikPollAsyncResult playbook is deployed before deploying RubrikAnomalyGenerateDownloadableLink playbook.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Enter the playbook name here.
    * Teams Group Id: Id of the Teams Group where the adaptive card will be posted
    * Teams Channel Id: Id of the Teams Channel where the adaptive card will be posted
    * PollAsyncResultPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikGenerateDownloadableLink%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikGenerateDownloadableLink%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like keyvault, azureloganalytics.
1. Go to your logic app -> API connections -> Select teams connection resource
2. Go to General -> edit API connection
3. Click the keyvault connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for other connections

#### b. Assign Role to add a comment in the incident

After authorizing each connection, assign a role to this playbook.
1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles
4. Role: Microsoft Sentinel Contributor
5. Members: select managed identity for "assigned access to" and add your logic app as a member.
6. Click on review+assign
