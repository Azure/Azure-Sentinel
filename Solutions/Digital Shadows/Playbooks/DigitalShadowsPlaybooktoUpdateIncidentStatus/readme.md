# DigitalShadowsPlaybook-UpdateIncidentStatus

## Overview

The DigitalShadowsPlaybook-UpdateIncidentStatus is run as an Alert automation by Analytics Rules created as part of the Digital Shadows SearchLight Solution. The main purpose of the playbook is to update the Microsoft Sentinel Incident Status as per the logs received by the Digital Shadows Data Connector. Following is the sequence of events take place for triggering the playbook:

1. Digital Shadows Data Connector fetches the Triage Items from Digital Shadows Searchlight portal
1. The Analytic Rule identifies an update in the Triage Item as an alert
1. Each alert with new triage item (identified by the unique triage item id) generates a Microsoft Sentinel Incident
1. All the updates detected by Analytic Rule are identified as alerts and correlated with an incident if the Incident (with same triage item id) already exists
1. Creation of an alert triggers the "DigitalShadowsPlaybook-UpdateIncidentStatus" playbook as an Alert automation, so that the "Status" of the incident, associated with alert's triage item id, is updated

## Playbook Workflow

Following is the workflow of the playbook:

1. Playbook is triggered on alert creation
2. Get incident associated with the alert
3. Get the custom details from the alert
4. Retrieve the updated value for Status
5. Update the Incident Status by mapping the Digital Shadows Status to corresponding Microsoft Sentinel Incident Status

## Prerequisite

This playbook is intended to be used with the Digital Shadows Data Connector and is typically installed as part of the Digital Shadows SearchLight Solution. It is not intended to be used standalone.

If installing manually, for use with the Digital Shadows Data Connector, it needs to be deployed under the same subscription.

Digital Shadows SearchLight API credentials are required to configure the connector.

## Deploying the Playbook manually

As described above, this playbook is intended to be used as part of the Digital Shadows Solution and not standalone. The following instructions enable users to manually install the playbook if required.

1. To deploy the Playbook, click the "Deploy to Azure" button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Playbook Name: Enter the playbook name here, a default is provided

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDigital%20Shadows%2FPlaybooks%2FDigitalShadowsPlaybook-UpdateIncidentStatus.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDigital%20Shadows%2FPlaybooks%2FDigitalShadowsPlaybook-UpdateIncidentStatus.json)

## Post-deployment instructions

### Configuring role assignment

Once deployment is complete, the playbook requires the 'Microsoft Sentinel Responder' role in order to be able to update the status of Incidents.

- Go to Microsoft Sentinel > Settings
- Click "Workspace settings" to navigate to the Log Analytics workspace
- Click "Access control (IAM)"
- Click "Add" > Add role assignment
- Select "Microsoft Sentinel Responder" from the list of Roles and click "Next"
- On the "Members" tab
  - Assign access to: Managed identity
  - Click "Select members"
  - In the pop-out menu, click the "Managed identity" drop down and select "Logic app"
  - Select the Logic app named "DigitalShadowsPlaybook-UpdateIncidentStatus" and click the Select button
- Optionally provide a description such as "Provide access to the Digital Shadows UpdateIncidentStatus playbook to update the status of Microsoft Sentinel Incidents from changes in Digital Shadows SearchLight Portal".
- Click "Review + assign" twice to create the new role assignment

### Configuring the Analytic Rule

Once deployment is complete, the Digital Shadows Analytics Rules need to be configured with the playbook as an Alert automation.

- Go to Microsoft Sentinel > Analytics
- The Digital Shadows Solution usually creates two Analytics Rules. Both need to be updated in the same way
- Select a rule and click on the "Edit" button
- Skip to the Automated response section
- Under "Alert automation" select the "DigitalShadowsPlaybook-UpdateIncidentStatus" playbook in the drop down
- Leave the remaining settings on the page unchanged
- Save the Analytic Rule

Repeat these instructions for the other Analytic Rule. This will execute the playbook automatically when new alerts are created by the Digital Shadows Analytic Rules.