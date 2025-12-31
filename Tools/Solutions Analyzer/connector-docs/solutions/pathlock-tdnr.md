# Pathlock_TDnR

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Pathlock Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://pathlock.com/support/](https://pathlock.com/support/) |
| **Categories** | domains,verticals |
| **First Published** | 2022-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Pathlock Inc.: Threat Detection and Response for SAP](../connectors/pathlock-tdnr.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ABAPAuditLog`](../tables/abapauditlog.md) | [Pathlock Inc.: Threat Detection and Response for SAP](../connectors/pathlock-tdnr.md) | - |
| [`Pathlock_TDnR_CL`](../tables/pathlock-tdnr-cl.md) | [Pathlock Threat Detection and Response Integration](../connectors/pathlock-tdnr.md) | - |

## Additional Documentation

> 📄 *Source: [Pathlock_TDnR/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR/README.md)*

This project provides an ARM template to deploy the "Pathlock Threat Detection & Response (TD&R)" connector in Microsoft Sentinel Solution for SAP. The deployment includes the following components:
- Connector
- Workbook
- Parser Function

## Deployment via Content Hub

To deploy using the Content Hub:

1. Log in to the Azure Portal.
2. Navigate to Microsoft Sentinel and select your workspace.
3. Go to **Content Hub**.
4. Search for **Pathlock Threat Detection & Response (TD&R)**.
5. Click **Install**, then **Create**.
6. Follow the prompts to complete the installation.

## Deployment via ARM Template

If the connector is not yet available in the Content Hub, you can deploy it manually using the provided ARM template.

### Prerequisites

- Access to the Microsoft Sentinel environment.
- Workspace name and location (found in Sentinel > Settings > Workspace Settings > Properties > Location).
- Microsoft Sentinel Agent installed on the relevant system.
- Path for log file generation.
- Cron job configured to append new logs to an existing file.
- Logs must be received in a custom table named `Pathlock_TDnR_CL`.

### Installation Steps

1. Click the **Deploy to Azure** button below.
2. Select the Resource Group where Microsoft Sentinel is deployed.
3. Enter the Microsoft Sentinel Workspace name.
4. Leave other settings as default.
5. Click **Review + create**.
6. Wait for validation, then click **Create**.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Ffrozenstrawberries%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPathlock_TDnR%2FPackage%2FmainTemplate.json)

---

*This solution is provided by Pathlock as a temporary deployment method until the official connector is available in the Content Hub.*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       |  05-11-2025                    | Initial Solution Release					 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
