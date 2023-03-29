# ProofpointTAP-AddForensicsInfoToIncident
 ## Summary
 Once a new sentinel incident is created, this playbook gets triggered and performs the following actions:
 1. [Gets Forensics](https://help.proofpoint.com/Threat_Insight_Dashboard/API_Documentation/Forensics_API) by the *campaignId*, provided in the alert custom entities. 
 2. Enriches the incident with Forensics info.

<img src="./playbook_screenshot.png" width="80%"/><br>
### Prerequisites 
1. ProofpointTAP Custom Connector has to be deployed prior to the deployment of this playbook under the same subscription.
2. ProofpointTAP API credentials are required. Refer to ProofpointTAP Custom Connector documentation.

### Deployment instructions 
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FProofPointTap%2FPlaybooks%2FProofpointTAP-AddForensicsInfoToIncident%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FProofPointTap%2FPlaybooks%2FProofpointTAP-AddForensicsInfoToIncident%2Fazuredeploy.json)


### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for Proofpoint TAP connector API Connection. Provide the Service Principal and the secret for authorizing.
#### b. Configurations in Sentinel
1. In Azure sentinel, analytical rules should be configured to trigger an incident. An incident should have *campaignId* custom entity (obtained from *campaignId_s* field in ProofpointTAP logs). Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom entities to incidents. 
2. Configure the automation rules to trigger the playbook.
