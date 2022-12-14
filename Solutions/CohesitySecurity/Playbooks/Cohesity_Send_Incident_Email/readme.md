# Cohesity Send Incident Email
## Summary
This playbook sends an email to the recipient with the incident details..

## Prerequisites
1. Create a distribution list (email) that will be used for sending out incident notifications.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FCohesity_Send_Incident_Email%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name__: Playbook display name.

## Post-Deployment instructions
To update the email address in the playbook:
* In your Microsoft Sentinel workspace, go to the _Automation_ under the _Configuration_ pane.
* Under _Active Playbooks_, select the playbook and click on _Edit_.
* On the _Logic App Designer_ page, select _Initialize variable 2_.
* Under the value section, enter the email address for the incident notifications.
* Click _Save_.

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
