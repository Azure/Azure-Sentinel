# Create Incident in Service Now Playbook
## Summary
This playbook creates a ticket in ServiceNow

## Prerequisites
1. Cohesty SIEM/SOAR integration needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Have a valid account for ServiceNow

## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)

2. Fill in the required parameters:
* Playbook Name: Enter the playbook name here
* ServiceNow URL: Enter the HTTP-address of your ServiceNow instance
* ServiceNow Login: Enter your ServiceNow login
* ServiceNow Password: Enter your ServiceNow password

## Post-Deployment instructions
* None

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
