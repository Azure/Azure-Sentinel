# ReversingLabs-EnrichFileHash

Author: Aaron Hoffmann (ReversingLabs)

## Summary
This playbook enriches file hash entities with information from the ReversingLabs TitaniumCloud API.

## Prerequisites

You'll need the following:
* A ReversingLabs TitaniumCloud subscription
* A ReversingLabs TitaniumCloud username
* A ReversingLabs TitaniumCloud password


## Deployment instructions
1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FReversingLabs%2FPlaybooks%2FReversingLabs-EnrichFileHash%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FReversingLabs%2FPlaybooks%2FReversingLabs-EnrichFileHash%2Fazuredeploy.json)

## Post-deployment

a. Authorize connections (Perform this action if needed)
Once deployment is complete, you will need to authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for the ReversingLabs TitaniumCloud Connection (For authorizing the connection, a TitaniumCloud username and password needs to be provided)

## Screenshots

![Playbook overview](./images/playbook.png)

## References

- [ReversingLabs content pack installation guide](https://reversinglabs-marketplace.azureedge.net/help/ReversingLabsSentinelContentHubInstall.pdf)
- [Video - How to install and configure the ReversingLabs content pack](https://www.youtube.com/watch?v=gLjMDz618O0)