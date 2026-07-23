# SpectraAnalyze-EnrichNetworkEntities

Author: Aaron Hoffmann (ReversingLabs)

## Summary
This playbook enriches network entities (IP addresses, URLs, and domains) with information from a ReversingLabs Spectra Analyze (formerly A1000) appliance.

## Prerequisites

You'll need the following:
* A ReversingLabs Spectra Analyze host URL
* A ReversingLabs Spectra Analyze API token


## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FReversingLabs%2FPlaybooks%2FSpectraAnalyze-EnrichNetworkEntities%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FReversingLabs%2FPlaybooks%2FSpectraAnalyze-EnrichNetworkEntities%2Fazuredeploy.json)

## Post-deployment

After deploying the template, you'll want to update the playbook connections with your Spectra Analyze API token.

## Screenshots

![Playbook overview](./playbook.png)

## References

- [ReversingLabs content pack installation guide](https://reversinglabs-marketplace.azureedge.net/help/ReversingLabsSentinelContentHubInstall.pdf)
- [Video - How to install and configure the ReversingLabs content pack](https://www.youtube.com/watch?v=gLjMDz618O0)