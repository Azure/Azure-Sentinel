# Azure DevOps Microsoft Sentinel Connector

Author: Rogier Dijkman

The Azure DevOps Auditing Sentinel connector provides the capability to ingest Azure DevOps events in Microsoft Sentinel.
It helps you gain visibility into what is happening in your environment, such as who is connected, which applications are installed and running, and much more.

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FAzureDevOpsAuditing%2FmainTemplate.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FAzureDevOpsAuditing%2FuiMainTemplate.json)

## Configuring the Azure DevOps Audit Streams

There are several options to configure the Audit Stream in Azure DevOps.
The possible options can also be found in the Data Connector after this has been deployed to Microsoft Sentinel.

### Option 1 - Azure Resource Manager (ARM) Template

Use this method for automated configuration of the data connector using an ARM Template.

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FAzureDevOpsAuditing%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FAzureDevOpsAuditing%2FUiDefinition.json)

### Option 2 - PowerShell onboarding

```powershell
$workspaceId = "*****"
$workspaceKey = "*****"
$organization = "MyOrganization"
$pattoken = "*****"

Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/AzureDevOpsAuditing/scripts/Set-AzureDevOpsAuditing.ps1' -OutFile 'Set-AzureDevOpsAuditing.ps1' && .\/Set-AzureDevOpsAuditing.ps1 -workspaceId $workspaceId -workspaceKey $workspaceKey -organization $organization -personalaccesstoken $pattoken
```

## Prerequisites

Personal Access Token (pattoken) with the following permissions:

- Manage Audit Streams
- Read Audit Log
- Role Assignment Permissions in Azure (this is used to create the managed identity)

## Created Resources

This deployment will create the following resources tot configure Audit Streams in Azure DevOps

- Managed Identity
- Azure Key Vault
- Deployment Script

### Azure Key Vault

The template will deploy an Azure Key Vault to securely store the provided Personal Access Token. This token will later be used to configure the audit stream.

### Managed Identity

A Managed Identity is created within the subscription for the purpose of running a deployment script within Microsoft Azure.
After the deployment of de data connector has completed, the Managed Identity can be removed.

### Deployment Script

During the deployment of the ARM template, a deployment script will be created.
This deployment script has the logic for creating and configuring streams within Azure DevOps.

## Validate Stream

After configuring the Audit Streams in Azure DevOps the audit connectivity should be visible in the Microsoft Sentinel Portal

## Detection Rules

Microsoft already has some build-in detection and hunting rules for Azure DevOps which can be found in the [Microsoft Sentinel GitHub](https://github.com/Azure/Azure-Sentinel/tree/master/Detections/AzureDevOpsAuditing) repository.
