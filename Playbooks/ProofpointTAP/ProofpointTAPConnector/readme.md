# Proofpoint TAP Logic Apps Custom connector

<img src="./CarbonBlack.PNG" alt="drawing" width="20%"/><br>

This custom connector connects to Proofpoint TAP API.

### Authentication methods this connector supports

*  Basic authentication

### Prerequisites in Proofpoint TAP
1. Get Proofpoint TAP API credentials ([learn how](LINK_TO_PP_TAP_AUTH_DOC))


## Actions supported by Proofpoint TAP custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get Forensics** | Pull detailed forensic evidences about individual threats  or campaigns |
| **Get campaign by id** | Pull specific details about campaigns, including: their description; the actor, malware family, and techniques associated with the campaign; and the threat variants which have been associated with the campaign |
| **Get Very Attacked People** | Fetch the identities and attack index breakdown of Very Attacked People within your organization for a given period. |
| **Get top clickers** | Fetch the identities and attack index breakdown of Very Attacked People within your organization for a given period. |
| **Decode a URL** | Decode URLs which have been rewritten by TAP to their original, target URL |



### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fproofpoint_tap_logic_app%2FPlaybooks%2FProofpointTAP%2FProofpointTAPConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fproofpoint_tap_logic_app%2FPlaybooks%2FProofpointTAP%2FProofpointTAPConnector%2Fazuredeploy.json)
