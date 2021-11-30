# Get-TenableVlun

Author: Younes Khaldi

This playbook will get vulnerability data from tenanble.io instance and send it to log analytics workspace.

# Pre-Requisites:


- Onboarding Azure Sentinel. Ref https://docs.microsoft.com/azure/sentinel/quickstart-onboard<br>
- Tenable.io vulnerability management up and running
- Tenable.io API Key: https://docs.tenable.com/tenableio/vulnerabilitymanagement/Content/Settings/GenerateAPIKey.htm
- Tenable.io API Ref  https://developer.tenable.com/reference
- Configuring Security Playbook using Azure Logic App. Ref https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-TenableVlun%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-TenableVlun%2Fazuredeploy.json)