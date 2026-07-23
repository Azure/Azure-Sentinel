# Advanced Security Information Model (ASIM)

The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)

For a list of parsers that currently exist, see [List of Microsoft Sentinel Advanced Security Information Model (ASIM) parsers](https://learn.microsoft.com/en-us/azure/sentinel/normalization-parsers-list).

## Copilot Agent Skills for ASIM Parser Creation

GitHub Copilot agent skills are available to help you create, validate, deploy, and package ASIM parsers locally. The skills guide you through the full workflow — from gathering requirements and generating KQL parsers to deploying to Log Analytics and opening a PR.

See [ASIM Parser Creation - Agentic](tools/ASIMParserCreation-Agentic/README.md) to get started.

## Deploy ASIM

This template deploys all [ASIM](https://aka.ms/AboutASIM) parsers.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2FASimFullDeployment.json)

[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2FASimFullDeployment.json)

To deploy a single schema use the buttons below:

| ASim Schema | Deploy | Deploy to Azure Gov |
| --------------- |-------------|--------|
|[Agent Event](https://aka.ms/ASimAgentEventDoc)| No parsers exist yet | No parsers exist yet
|[Alert Event](https://aka.ms/ASimAlertEventDoc)|[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimAlertEventARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimAlertEventARMgov) |
|[Asset Entity](https://aka.ms/ASimAssetEntityDoc)| No parsers exist yet| No parsers exist yet |
| [Audit Event](https://aka.ms/ASimAuditEventDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimAuditEventARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimAuditEventARMgov) |
| [Authentication](https://aka.ms/ASimAuthenticationDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimAuthenticationARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimAuthenticationARMgov) |
| [Dhcp Event](https://aka.ms/ASimDhcpEventDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimDhcpEventARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimDhcpEventARMgov) |
| [Dns](https://aka.ms/ASimDnsDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimDnsARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimDnsARMgov) |
| [File Event](https://aka.ms/ASimFileEventDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimFileEventARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimFileEventARMgov) |
| [Network Session](https://aka.ms/ASimNetworkSessionDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimNetworkSessionARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimNetworkSessionARMgov) |
| [Process Event](https://aka.ms/ASimProcessEventDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimProcessEventARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimProcessEventARMgov) |
| [Registry Event](https://aka.ms/ASimRegistryEventDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimRegistryEventARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimRegistryEventARMgov) |
| [UserManagement](https://aka.ms/ASimUserManagementDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimUserManagementARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimUserManagementARMgov) |
| [Web Session](https://aka.ms/ASimWebSessionDoc) | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimWebSessionARM)| [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://aka.ms/ASimWebSessionARMgov)|