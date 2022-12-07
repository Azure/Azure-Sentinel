# Send Incident Email
## Summary
This playbook sends an email to the recipient with the details related to the incidents.

## Prerequisites
1. Cohesty SIEM/SOAR integration needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Distribution list that will be used for sending out incident notifications, should be created.

## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2Fcohesity%2FAzure-Sentinel%2Ftree%2Fmaster%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FIncident_Email_Playbook%2Fazuredeploy.json)

2. Fill in the required parameters:
* __Playbook Name__: Enter the playbook name here
* __Email address__: The distribution list for incident notifications

## Post-Deployment instructions
None

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
