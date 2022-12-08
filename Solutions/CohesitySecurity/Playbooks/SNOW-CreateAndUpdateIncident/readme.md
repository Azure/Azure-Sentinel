# Cohesity Create or Update ServiceNow Incident 
## Summary
This playbook creates a ticket in ServiceNow.

## Prerequisites
1. Create an account for [ServiceNow](https://signon.service-now.com/x_snc_sso_auth.do).

## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2Fcohesity%2FAzure-Sentinel%2Fblob%2FCohesitySecurity.internal%2FSolutions%2FCohesitySecurity%2FPlaybooks%2FSNOW-CreateAndUpdateIncident%2Fazuredeploy.json)
2. Fill in the required parameters:
* __Playbook Name:__ Enter the playbook name here.
* __ServiceNow URL:__ Enter the HTTP-address of your ServiceNow instance.
* __ServiceNow Login:__ Enter your ServiceNow login.
* __ServiceNow Password:__ Enter your ServiceNow password.

## Post-Deployment instructions
* None

#  References
 - [Cohesity support documentation](https://docs.cohesity.com/ui/login?redirectPath=%2FHomePage%2FContent%2FTechGuides%2FTechnicalGuides.htm)
