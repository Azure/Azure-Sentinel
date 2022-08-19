# Proofpoint TAP Logic Apps Custom connector

<img src="./proofpointlogo.png" alt="drawing" width="20%"/><br>

This custom connector connects to Proofpoint TAP API.

### Authentication methods this connector supports

*  Basic authentication

### Prerequisites in Proofpoint TAP
To get Proofpoint TAP API credentials follow the instructions:
1. Login to your Proofpoint TAP dashboard.
2. Click the *Settings* tab.
3. Click *Connected Applications*.
4. In the *Name* section, select *Create New Credential*.
5. Type the name and click the *Generate* button.
6. In the *Generated Service Credential* pop-up, the *Service Principal* and *Secret* values are shown.


## Actions supported by Proofpoint TAP custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get Forensics** | Pull detailed forensic evidences about individual threats  or campaigns |
| **Get campaign by id** | Pull specific details about campaigns, including: their description; the actor, malware family, and techniques associated with the campaign; and the threat variants which have been associated with the campaign |
| **Get Very Attacked People** | Fetch the identities and attack index breakdown of Very Attacked People within your organization for a given period. |
| **Get top clickers** | Fetch the identities and attack index breakdown of Very Attacked People within your organization for a given period. |
| **Decode a URL** | Decode URLs which have been rewritten by TAP to their original, target URL |



### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FProofPointTap%2FPlaybooks%2FProofpointTAPConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FProofPointTap%2FPlaybooks%2FProofpointTAPConnector%2Fazuredeploy.json)
