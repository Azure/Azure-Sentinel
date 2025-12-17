# Morphisec API Data Connector (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `MorphisecCCF` |
| **Publisher** | Morphisec |
| **Tables Ingested** | [`MorphisecAlerts_CL`](../tables-index.md#morphisecalerts_cl) |
| **Used in Solutions** | [Morphisec](../solutions/morphisec.md) |
| **Connector Definition Files** | [Morphisec_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Morphisec/Data%20Connectors/Morphisec_CCF/Morphisec_ConnectorDefinition.json) |

The [Morphisec](https://www.morphisec.com/) solution for Microsoft Sentinel enables you to seamlessly ingest security alerts directly from the Morphisec API. By leveraging Morphisec's proactive breach prevention and moving target defense capabilities, this integration enriches your security operations with high-fidelity, low-noise alerts on evasive threats.

This solution provides more than just data ingestion; it equips your security team with a full suite of ready-to-use content, including: Data Connector, ASIM Parser, Analytic Rule Templates and Workbook.

With this solution, you can empower your SOC to leverage Morphisec's powerful threat prevention within a unified investigation and response workflow in Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure Morphisec Connector**

1. Create an API key client in Morphisec Console with read permissions to fetch alerts. 
2. Provide the Client ID and Client Secret in the connector configuration.
- **Morphisec Base URL**: https://<your-morphisec-region>.morphisec.cloud
- **Client ID**: Enter the Client ID
- **Client Secret**: (password field)
- **Tenant ID**: Enter your Morphisec Tenant ID
- Click 'Connect to Morphisec' to establish connection

[← Back to Connectors Index](../connectors-index.md)
