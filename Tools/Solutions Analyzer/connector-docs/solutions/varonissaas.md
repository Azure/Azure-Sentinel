# VaronisSaaS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Varonis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varonis.com/resources/support](https://www.varonis.com/resources/support) |
| **Categories** | domains |
| **First Published** | 2023-11-10 |
| **Last Updated** | 2023-11-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Varonis SaaS](../connectors/varonissaas.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`VaronisAlerts_CL`](../tables/varonisalerts-cl.md) | [Varonis SaaS](../connectors/varonissaas.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [VaronisSaaS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS/Workbooks/VaronisSaaS.json) | [`VaronisAlerts_CL`](../tables/varonisalerts-cl.md) |

## Additional Documentation

> 📄 *Source: [VaronisSaaS/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS/README.md)*

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
| Azure function app code       | https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/VaronisSaaS/Data%20Connectors/VaronisSaaSFunction |
| Log Analytics table(s)        | VaronisAlerts_CL                              |
| Data collection rules support | Not currently supported                       |
| Supported by                  | Varonis Corporation                           |

## Query samples
#### All Varonis Data Alerts logs

```kusto
VaronisAlerts_CL
| sort by TimeGenerated desc
```

## Prerequisites
To integrate with Varonis SaaS (using Azure Functions) make sure you have the following:
- Microsoft.Web/sites permissions: Read and write permissions to Azure Functions to create a Function App is required. See the [documentation](https://learn.microsoft.com/azure/azure-functions/) to learn more about Azure Functions.
- Varonis API credentials: Varonis API credentials with permission read log is required for Varonis SaaS API. See the documentation to learn more about creating Varonis SaaS API credentials.

## Vendor installation instructions
>This connector uses Azure Functions to connect to the Varonis SaaS Endpoint API to pull logs into Microsoft Sentinel. This might result in additional data ingestion costs. Check the [Azure Functions pricing page](https://azure.microsoft.com/pricing/details/functions/) for details.

STEP 1 - Obtain the Varonis DatAlert Endpoint API credentials.

To generate the Client ID and API key:

1. Launch the Varonis Web Interface.
2. Navigate to Configuration -> API Keys. The API Keys page is displayed.
3. Click Create API Key. The Add New API Key settings are displayed on the right.
4. Fill in the name and description.
5. Click the Generate Key button.
6. Copy the API key secret and save it in a handy location. You won't be able to copy it again.

For additional information, please check: [Varonis Documentation](https://help.varonis.com/s/document-item?bundleId=ami1661784208197&topicId=emp1703144742927.html&_LANG=enus)

STEP 2 - Deploy the connector and the associated Azure Function.

1. Click the Deploy to Azure button.\

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 25-11-2025                     | Add Informational severity level support    |
| 3.0.2       | 12-09-2025                     | Save last alert ingest time                 |
| 3.0.1       | 02-12-2025                     | Bug fixes                                   |
| 3.0.0       | 02-07-2024                     | Refactor azure function                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
