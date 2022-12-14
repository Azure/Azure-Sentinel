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
* __Email ID__: Email (preferably a distribution list) for sending out incident notifications

## Post-Deployment instructions
To update the email address in the playbook:
* In your Microsoft Sentinel workspace, go to the _Automation_ under the _Configuration_ pane.
* Under _Active Playbooks_, select the playbook and click on _Edit_.
* On the _Logic App Designer_ page, select _Initialize variable 2_.
* Under the value section, enter the email address for the incident notifications.
* Click _Save_.

## Troubleshooting
* If your playbook fails to send emails, go to _Logic Apps_, click on the playbook and press _Edit_. After that choose _Send an email (V2)_ block, click on _Change Connection_, select a different connection and press _Save_ button to save changes in your playbook. Then try again. If it doesn't work, then try another connection. Also, your playbook _Overview_ pane has status of all runs. By looking at the details, you can get more ideas on what could go wrong. 

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
