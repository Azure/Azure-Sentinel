# QCryptonPQCScannerAgent-Notify

## Overview

This playbook posts a notification card to a Microsoft Teams channel when a Microsoft Sentinel incident is created by one of the QCrypton PQC Scanner Agent analytic rules. The card includes the incident title, severity, and a direct link to the incident in the Sentinel portal.

## Prerequisites

- A Microsoft Teams team and channel where notifications should be posted.
- The Teams Group ID and Channel ID for the target channel (obtainable from the Teams admin center or the Microsoft Graph API).
- The Logic App managed identity must be granted the **Microsoft Sentinel Responder** role on the resource group containing the Sentinel workspace.

## Post-Deployment Instructions

1. After deployment, open the Logic App in the Azure portal.
2. Authorize the **Teams** API connection in the Logic App designer.
3. The **Azure Sentinel** connection uses managed identity and does not require manual authorization.

## Deploy the Playbook

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQCryptonPQCScannerAgent%2FPlaybooks%2FQCryptonPQCScannerAgent-Notify%2Fazuredeploy.json)
