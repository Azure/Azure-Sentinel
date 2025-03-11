# SpectraAnalyze-EnrichFileHash

Author: Aaron Hoffmann (ReversingLabs)

This playbook enriches file hash entities with information from a ReversingLabs Spectra Analyze (formerly A1000) appliance.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FReversingLabs%2FPlaybooks%2FSpectraAnalyze-EnrichFileHash%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FReversingLabs%2FPlaybooks%2FSpectraAnalyze-EnrichFileHash%2Fazuredeploy.json)
## Prerequisites

You'll need the following:
* A ReversingLabs Spectra Analyze Appliance URL
* A Spectra Analyze API Token


## Post-deployment

After deploying the template, you'll want to update the playbook connections with your Spectra Analyze API token.

## Screenshots

![Playbook overview](./playbook.jpg)

## References

- [ReversingLabs content pack installation guide](https://reversinglabs-marketplace.azureedge.net/help/ReversingLabsSentinelContentHubInstall.pdf)
- [Video - How to install and configure the ReversingLabs content pack](https://www.youtube.com/watch?v=gLjMDz618O0)