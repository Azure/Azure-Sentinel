# Microsoft Sentinel All-in-One

Microsoft Sentinel All-in-One is a project that seeks to speed up deployment and initial configuration tasks of an Microsoft Sentinel environments. This is ideal for Proof of Concept scenarios and customer onboarding in MSSP scenarios.

## What does it do?

Microsoft Sentinel All-In-One automates the following tasks:

- Creates resource group
- Creates Log Analytics workspace 
- Installs Microsoft Sentinel on top of the workspace
- Sets workspace retention, [daily cap](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/daily-cap) and commitment tiers if desired
- Enables UEBA with the relevant identity providers (AAD and/or AD)
- Enables health diagnostics for Analytics Rules, Data Connectors and Automation Rules
- Installs Content Hub solutions 
- Enables Data Connectors from this list: 
    + Azure Active Directory (only available in Tenant scope version)
    + Azure Active Directory Information Protection
    + Azure Activity
    + Dynamics 365
    + Microsoft 365 Defender
    + Microsoft Defender for Cloud
    + Microsoft Insider Risk Management
    + Microsoft Power BI
    + Microsoft Project
    + Office 365
    + Threat Intelligence Platforms
- Enables analytics rules (Scheduled and NRT) included in the selected Content Hub solutions
- Enables analytics rules (Scheduled and NRT) that use any of the selected Data connectors  

It takes around **10 minutes** to deploy if enabling analytics rules is selected. If enabling analytics rules is not needed, it will complete in around 2 minutes.

## Prerequisites

- Azure Subscription
- Azure user account with enough permissions to enable the desired connectors. See table at the end of this page for additional permissions. Write permissions to the workspace are **always** needed.
- Some data connectors require the relevant licence in order to be enabled. See table at the end of this page for details.

## Deployment

There are two versions of Microsoft Sentinel All-in-One:

| All-In-One version                                 | Deploy       | Permissions |
| -------------------------------------------------- | ------------ | -------- |
| Subscription scope                                 | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fallinonev2%2FTools%2FSentinel-All-In-One%2FSubscriptionLevel%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fallinonev2%2FTools%2FSentinel-All-In-One%2FSubscriptionLevel%2FcreateUiDefinition.json)   | Microsoft Sentinel Contributor as a minimum |
| Tenant scope (supports enabling Azure AD connector)     | [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fallinonev2%2FTools%2FSentinel-All-In-One%2FTenantLevel%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fallinonev2%2FTools%2FSentinel-All-In-One%2FTenantLevel%2FcreateUiDefinition.json)   | Need to grant permissions to deploy at tenant scope. [Learn more](https://learn.microsoft.com/azure/azure-resource-manager/templates/deploy-to-tenant?tabs=azure-cli#required-access). |  

## Supported connectors

The following table summarizes permissions, licenses and permissions needed and related cost to enable each Data Connector:

| Data Connector                                 | License         |  Permissions                    | Cost      |
| ---------------------------------------------- | --------------- |---------------------------------|-----------|
| Azure Active Directory (Tenant scope version only) | Any AAD license | Global Admin or Security Admin  | Billed    |
| Azure Active Directory Information Protection  | AAD Premium 2   | Global Admin or Security Admin  | Free      |
| Azure Activity                                 | None            | Subscription Reader             | Free      |
| Dinamycs 365                                   | D365 license    | Global Admin or Security Admin  | Billed    |
| Microsoft 365 Defender                         | M365D license   | Global Admin or Security Admin  | Free      |
| Microsoft Defender for Cloud                   | MDC license     | Security Reader                 | Free      |
| Microsoft Insider Risk Management              | IRM license     | Global Admin or Security Admin  | Free      |
| Microsoft PowerBi                              | PowerBi license | Global Admin or Security Admin  | Billed    |
| Microsoft Project                              | MS Project license | Global Admin or Security Admin | Billed  |
| Office 365                                     | None            | Global Admin or Security Admin  | Free      |
| Threat Intelligence Platforms                  | None            | Global Admin or Security Admin  | Billed    |

