# Varonis SaaS

### In this article
[Connector Attributes](#connector-attributes)\
[Connector Attributes](#query-samples)\
[Prerequisites](#prerequisites)\
[Vendor Installation Instructions](#vendor-installation-instructions)\
[Next Steps](#next-steps)

Varonis SaaS provides the capability to ingest [Varonis Alerts](https://www.varonis.com/products/SaaS) into Microsoft Sentinel.

Varonis prioritizes deep data visibility, classification capabilities, and automated remediation for data access. Varonis builds a single prioritized view of risk for your data, so you can proactively and systematically eliminate risk from insider threats and cyberattacks.

## Connector Attributes
| Connector attribute           | Description                                   |
| ----------------------------- | --------------------------------------------- |
| Connector type                | Codeless Connector Framework (CCF) Push       |
| Log Analytics table(s)        | VaronisAlertsV2_CL                            |
| Data collection rules support | Supported (DCR stream `Custom-VaronisSaaSAlerts`) |
| Supported by                  | Varonis Corporation                           |

## Query samples
#### All Varonis alerts

```kusto
VaronisAlertsV2_CL
| sort by TimeGenerated desc
```

## Prerequisites
To integrate with Varonis SaaS (Push) make sure you have the following:
- Workspace: read, write and delete permissions on the Log Analytics workspace.
- Microsoft Entra: permission to create an app registration (typically the Application Developer role or higher).
- Microsoft Azure: permission to assign the Monitoring Metrics Publisher role on the data collection rule (typically the Owner or User Access Administrator role).

## Vendor installation instructions
>This connector uses the Codeless Connector Framework (CCF) Push pattern. Varonis SaaS pushes DatAlert alerts to Microsoft Sentinel through the Azure Monitor Logs Ingestion API.

STEP 1 - Create the Azure resources.

1. In Microsoft Sentinel, open **Data connectors** and select **Varonis SaaS (Push)**.
2. Click **Deploy Varonis SaaS Push connector resources**. This creates the `VaronisAlertsV2_CL` table, a data collection rule, and a Microsoft Entra application with a client secret, and grants the application the Monitoring Metrics Publisher role on the data collection rule.

STEP 2 - Configure your Varonis SaaS application.

Copy the following values from the connector page into your Varonis SaaS application configuration:
- Tenant ID (Directory ID)
- Entra App Registration Application ID
- Entra App Registration Secret
- Data Collection Endpoint Uri
- Data Collection Rule Immutable ID
- Stream Name (`Custom-VaronisSaaSAlerts`)

## Next
For more information, go to the related solution in the Azure Marketplace.