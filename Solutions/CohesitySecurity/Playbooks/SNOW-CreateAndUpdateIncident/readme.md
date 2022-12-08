# Cohesity Create or Update ServiceNow Incident 
## Summary
This playbook creates a ticket in ServiceNow.

## Prerequisites
1. Create an account for [ServiceNow](https://signon.service-now.com/x_snc_sso_auth.do).

## Deployment instructions
1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcohesity%2FAzure-Sentinel%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FSNOW-CreateAndUpdateIncident%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.

## Post-Deployment instructions
1. Update ServiceNow credentials in the playbook
* In your Microsoft Sentinel Instance, go to the _Automation_ under the _Configuration_ pane.
* Under _Active Playbooks_, select the playbook and click on _Edit_.
* Select the ServiceNow connector on the _Logic App Designer_ page.
* Enter your ServiceNow instance credentials - URL, login and password.
* Select _Save_.
2. For the playbook to run, there is a need to assign the Microsoft Sentinel Responder role to the playbook's managed identity.
* Under the _Subscriptions_ tab from the _Home_ page, choose your subscription name.
* Choose the _Access Control (IAM)_ option from the left pane.
* Click on _Add > Add Role Assignment_ and add Microsoft Sentinel Responder managed identity role to the playbook. 

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
