# Incident Email Playbook
## Summary
This playbook sends emails with all incident details to everyone who needs to participate in the investigation.

## Prerequisites
1. Cohesty SIEM/SOAR integration needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Create a distribution list that will be used for sending out incident notifications.

## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)

2. Fill in the required parameters:
* Playbook Name: Enter the playbook name here
* Email address: The distribution list for incident notifications

## Post-Deployment instructions
None

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
