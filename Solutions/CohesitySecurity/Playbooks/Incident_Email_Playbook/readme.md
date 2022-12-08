# Send Incident Email
## Summary
This playbook sends an email to the recipient with the incident details..

## Prerequisites
1. Create a distribution list (email) that will be used for sending out incident notifications.

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FIncident_Email_Playbook%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name__: Playbook display name.
* __Email address__: Distribution list (email) for incident notifications (not yet implemented; see post-deployment instructions below)

## Post-Deployment instructions
To update the email address in the playbook:
* In your Microsoft Sentinel Instance, go to the Automation under the Configuration pane.
* Under Active Playbooks, select the playbook and click on Edit.
* On the Logic App Designer page, select Initialize variable 2.
* Under the value section, enter the email address for the incident notifications.
* Select Save.

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
