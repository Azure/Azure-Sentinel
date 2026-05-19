
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
