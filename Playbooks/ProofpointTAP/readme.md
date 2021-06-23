  # Proofpoint TAP Logic Apps connector and playbook templates

  <img src="./ProofpointTAPConnector/proofpointlogo.png" alt="drawing" width="20%"/><br>


## Table of Contents

1. [Overview](#overview)
1. [Deploy Custom Connector + 3 Playbook templates](#deployall)
1. [Authentication](#importantnotes)
1. [Prerequisites](#prerequisites)
1. [Deployment](#deployment)
1. [Post Deployment Steps](#postdeployment)
1. [References](#references)
1. [Known issues and limitations](#limitations)


<a name="overview">

# Overview

Proofpoint is a cybersecurity platform aimed to protect workers and data from advanced cybersecurity criminals that target email, social media and mobile devices. Proofpoint offers a wide variety of products, in addition to email protection to enhance a company's security.

<a name="deployall">

## Deploy Custom Connector + 3 Playbook templates
This package includes:
* [Logic Apps custom connector for Proofpoint TAP](./ProofpointTAPConnector)

* Three playbook templates leverage Proofpoint TAP custom connector:
  * [Enrichment – add information to incidents](./Playbooks/ProofpointTAP-CheckAccountInVAP) - check if user is in the Very Attacked People list. Post information about the incident as a comment to the incident.
  * [Enrichment - add forensics info to incident](./Playbooks/ProofpointTAP-AddForensicsInfoToIncident) - collect information about the threat campaign and post it as incident comment.

You can choose to deploy the whole package: connector + all three playbook templates, or each one seperately from it's specific folder.


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fproofpoint_tap_logic_app%2FPlaybooks%2FProofpointTAP%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fproofpoint_tap_logic_app%2FPlaybooks%2FProofpointTAP%2Fazuredeploy.json)



# Proofpoint TAP connector documentation 

<a name="authentication">

## Authentication
This connector supports Basic authentication. When creating the connection for the custom connector, you will be asked to provide the Service Principal and the Secret which you generated in Proofpoint TAP platform. 

<a name="prerequisites">

### Prerequisites in Proofpoint TAP
To get Proofpoint TAP API credentials follow the instructions:
1. Login to your Proofpoint TAP dashboard.
2. Click the *Settings* tab.
3. Click *Connected Applications*.
4. In the *Name* section, select *Create New Credential*.
5. Type the name and click the *Generate* button.
6. In the *Generated Service Credential* pop-up, the *Service Principal* and *Secret* values are shown.

<a name="deployment">

### Deployment instructions 
1. Deploy the Custom Connector and playbooks by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying custom connector and playbooks

| Parameters | Description |
|----------------|--------------|
|**For Playbooks**|
|**ProofpointTAP-CheckAccountInVAP Playbook Name** | Enter the playbook name here (e.g. ProofpointTAP-CheckAccountInVAP)|
|**ProofpointTAP-AddForensicsInfoToIncident Playbook Name** | Enter the playbook name here (e.g. ProofpointTAP-AddForensicsInfoToIncident)|

<br>
<a name="postdeployment">

### Post-Deployment instructions 
#### a. Authorize connections
Once deployment is complete, you will need to authorize each connection.
1.	Click the Azure Sentinel connection resource
2.	Click edit API connection
3.	Click Authorize
4.	Sign in
5.	Click Save
6.	Repeat steps for Proofpoint TAP connector API Connection (For authorizing, the Service Principal and the secret need to be provided.)
#### b. Configurations in Sentinel
1. In Azure sentinel analytical rules should be configured to trigger an incident with risky user account. 
2. Configure the automation rules to trigger the playbooks.


<a name="limitations">

## Known Issues and Limitations
