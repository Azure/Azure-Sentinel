# JuniperIDP

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JuniperIDP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JuniperIDP) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Juniper IDP](../connectors/juniperidp.md)

**Publisher:** Juniper

The [Juniper](https://www.juniper.net/) IDP data connector provides the capability to ingest [Juniper IDP](https://www.juniper.net/documentation/us/en/software/junos/idp-policy/topics/topic-map/security-idp-overview.html) events into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `JuniperIDP_CL` |
| **Connector Definition Files** | [Connector_LogAnalytics_agent_JuniperIDP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JuniperIDP/Data%20Connectors/Connector_LogAnalytics_agent_JuniperIDP.json) |

[→ View full connector details](../connectors/juniperidp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `JuniperIDP_CL` | [[Deprecated] Juniper IDP](../connectors/juniperidp.md) |

[← Back to Solutions Index](../solutions-index.md)
