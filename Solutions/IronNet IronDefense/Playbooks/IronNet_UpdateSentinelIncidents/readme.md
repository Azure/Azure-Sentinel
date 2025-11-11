# IronNet_UpdateSentinelIncidents
author: IronNet

This playbook is used to keep IronDefense and Azure Sentinel in sync by
triggering on any new IronDefense alert notifications that is added to a
Sentinel incident and updating the incident's status and classification based on
the IronDefense alert.

## Prerequisites
1. Configure the IronNet IronDefense data connector.
2. Create an analytic rule using the "Create Incidents from IronDefense" rule
   template.

## Deployment Instructions
1. Click the "Deploy to Azure" button to open the ARM template wizard to deploy
this playbook.<br>
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIronNet%20IronDefense%2FPlaybooks%2FIronNet_UpdateSentinelIncidents%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIronNet%20IronDefense%2FPlaybooks%2FIronNet_UpdateSentinelIncidents%2Fazuredeploy.json)
2. Enter template parameters. Use the IronVue user credentials for IronAPI.

## Playbook Execution
1. The Playbook execution begins with an Alert triggered due to the IronDefense 
   Alert activity
2. This Alert contains the actions taken by the IronDefense Alert
3. These actions will have the information about the status, classification and 
   severity of the Irondefense Alert
4. These details will be picked from the IronDefense and update to its corresponding 
   Sentinel Incidents
5. The Alerts from IronDefense will be the Events associated with the Sentinel Incidents
6. The Status, Classification and Severity of the Irondefense Alert will be updated as 
   the Sentinel Incident's status, classification and severity respectively
7. The Sentinel Incident's "custom details" will be consisting of IronDefense Analyst rating, 
   AlertCreatedTime and IronDefenseAlertId fields
8. The Sentinel Incident's comments will be updated with the comments raised by users for IronDome Notifications

