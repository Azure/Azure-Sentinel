# Restore From Last Snapshot Playbook
## Summary
This playbook restores the latest good Helios snapshot. It’s recommended for Backup Admins only after they make sure that the existing data are compromised.

## Prerequisites
1. Cohesty SIEM/SOAR integration needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Have the API Key for Helios.

## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)

2. Fill in the required parameters:
* Playbook Name: Enter the playbook name here
* Helios API Key: Enter the API key

## Post-Deployment instructions
* (Recommendation) Limit access rights to this playbook to only Backup Admins as running this playbook rolls back customer data that can result in a loss of data if used inappropriately.

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
