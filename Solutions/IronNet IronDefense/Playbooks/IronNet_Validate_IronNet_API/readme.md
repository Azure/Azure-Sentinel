# IronNet_ValidateIronAPI
author: IronNet

This playbook is used for validating IronAPI Endpoints.

## Deployment Instructions
1. Click the "Deploy to Azure" button to open the ARM template wizard to deploy
this playbook.<br>
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIronNet%20IronDefense%2FPlaybooks%2FIronNet_UpdateSentinelIncidents%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FIronNet%20IronDefense%2FPlaybooks%2FIronNet_UpdateSentinelIncidents%2Fazuredeploy.json)
2. Enter template parameters. Use the IronVue user credentials for IronAPI.

## Playbook Execution
1. The Playbook execution begins with an API call to IronDefense 
   Alert.
2. This workflow validates for 8 IronAPI endpoints inorder to verify that the 
   API is stable.
