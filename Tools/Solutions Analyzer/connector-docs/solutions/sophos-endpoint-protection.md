# Sophos Endpoint Protection

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Sophos Endpoint Protection](../connectors/sophosep.md)

**Publisher:** Sophos

### [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md)

**Publisher:** Microsoft

The [Sophos Endpoint Protection](https://www.sophos.com/en-us/products/endpoint-antivirus.aspx) data connector provides the capability to ingest [Sophos events](https://developer.sophos.com/docs/siem-v1/1/routes/events/get) and [Sophos alerts](https://developer.sophos.com/docs/siem-v1/1/routes/alerts/get) into Microsoft Sentinel. Refer to [Sophos Central Admin documentation](https://docs.sophos.com/central/Customer/help/en-us/central/Customer/concepts/Logs.html) for more information.

| | |
|--------------------------|---|
| **Tables Ingested** | `SophosEPAlerts_CL` |
| | `SophosEPEvents_CL` |
| **Connector Definition Files** | [SophosEP_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Sophos%20Endpoint%20Protection/Data%20Connectors/SophosEP_ccp/SophosEP_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/sophosendpointprotectionccpdefinition.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SophosEPAlerts_CL` | [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md) |
| `SophosEPEvents_CL` | [Sophos Endpoint Protection (using REST API)](../connectors/sophosendpointprotectionccpdefinition.md) |
| `SophosEP_CL` | [Sophos Endpoint Protection](../connectors/sophosep.md) |

[← Back to Solutions Index](../solutions-index.md)
