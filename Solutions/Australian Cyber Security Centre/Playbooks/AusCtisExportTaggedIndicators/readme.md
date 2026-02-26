# AusCtisExportTaggedIndicators

## Summary

This playbook gets triggered every day and perform the following actions:

1. Get all the threat intelligence indicators from Microsoft Sentinel Workspace with given tag.
2. Filter all the indicators whose export in not completed.
3. Verify/Add TLP labels to indicators.
4. Add Grouping and Identity Objects to indicators.
5. Export the bundle to provided TAXII server.

<img src="./images/Playbook_AusCtisExportTaggedIndicators_light.jpg" width="50%"/><br>

### Prerequisites

1. Have TAXII Server Url, Collection ID, Username and Password handy before the deployment of the Playbook

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name
    * TAXII Server Url
    * TAXII Server Username
    * TAXII Server Password
    * Collection ID
    * Orgnization UUID
    * Microsoft Sentinel Workspace
    * Tag for indicators to be exported
    * Tag for indicators after export completion
    * Default TLP Label

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAustralian%2520Cyber%2520Security%2520Centre%2FPlaybooks%2FAusCtisExportTaggedIndicators%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAustralian%2520Cyber%2520Security%2520Centre%2FPlaybooks%2FAusCtisExportTaggedIndicators%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize Playbook to access Log Analytics Workspace

Once deployment is complete, assign playbook Log Analytics contributor role.

1. Go to Log Analytics Workspace resource
2. Select Access control (IAM) tab
3. Add role assignments
4. Select Contributor role
5. In the Members tab choose "Assign access to" Managed Identity
6. Click on "Select members"
8. Provide correct Subscription and Managed Identity 
7. Provide the playbook name in "Search by name" textbox
8. Select the correct identity and click on Select
9. Click on "Review + assign" 


#  References
* [Australian Cyber Security Centre](https://www.cyber.gov.au/)