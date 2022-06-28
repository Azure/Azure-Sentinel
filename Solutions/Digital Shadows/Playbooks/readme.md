# DigitalShadowsPlaybook-UpdateIncidentStatus

## Overview
The DigitalShadowsPlaybook-UpdateIncidentStatus is triggered when an alert is created by the Digital Shadows Data Connector Analytic Rules. The main purpose of the playbook is to update the Microsoft Sentinel Incident Status as per the logs received by Data Connector. Following is the sequence of events take place for triggering the playbook:

1. Digital Shadows Data Connector fetches the Triage Items from Digital Shadows Searchlight portal
1. The analytic rule identifies an update in the Triage Item as an alert
1. Each alert with new triage item (identified by the unique triage item id) generates an Azure Sentinel Incident
1. All the updates detected by Analytic rule are identified as alerts and correlated with an incident if the Incident (with same triage item id) already exists
1. Creation of each alert triggers the "DigitalShadowsPlaybook-UpdateIncidentStatus" playbook so that the "Status" of the incident, associated with alert's triage item id, is updated

## Playbook Workflow
Following is the workflow of the playbook:
1. Playbook is triggered on alert creation
1. Get incident associated with the alert
1. Get the custom details from the alert
1. Retrieve the updated value for Status
1. Update the Incident Status by mapping the Digital Shadows Status to corresponding Azure Sentinel Incident Status

## Prerequisite
1. Prior to the deployment of this playbook, Digital Shadows Data Connector needs to be deployed under the same subscription.
1. Obtain Digital Shadows SearchLight API credentials from Digital Shadows. These credentials will be needed to configure the connector.

**Note**: This playbook is intended to be used with the Digital Shadows Data Connector and is not intended to be used standalone. When being used with the Digital Shadows Data Connector, it needs to be deployed under the same subscription. If the Playbook is to be deployed manually or as a standalone resource, please ignore the prerequisites.


## Deploying the Playbook
The Playbook is deployed with the Digital Shadows Data Connector. To deploy the Data connector, follow the below steps:
1. Go to Azure Sentinel -> Data Connectors
1. Click on the Digital Shadows connector, connector page will open. 
1. Click on the `Deploy to Azure` button.   

![Deploy to Azure](https://user-images.githubusercontent.com/88835344/143393168-018f97fb-95c1-4884-ba93-09306dd168b0.png)


It will lead to a custom deployment page where after entering accurate credentials and other information, the playbook will be created with other  resources. 

![Create resources](https://user-images.githubusercontent.com/88835344/142581668-5d5dd767-55a2-49fc-a9c9-eb458f75a2a7.png)


![Deploy to Azure](https://aka.ms/deploytoazurebutton)(https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDigital%20Shadows%2FPlaybooksk%2FDigitalShadowsPlaybook-UpdateIncidentStatus.json)