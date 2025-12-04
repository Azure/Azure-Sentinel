# Palo Alto - XDR (Cortex)

## Solution Information

| | |
|------------------------|-------|
| **Publisher** |  |
| **Support Tier** |  |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Palo Alto Networks Cortex XDR](../connectors/paloaltonetworkscortex.md)

**Publisher:** Palo Alto Networks

The Palo Alto Networks Cortex XDR connector gives you an easy way to connect to your Cortex XDR logs with Microsoft Sentinel. This increases the visibility of your endpoint security. It will give you better ability to monitor your resources by creating custom Workbooks, analytics rules, Incident investigation, and evidence gathering.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_PaloAlto_XDR_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Palo%20Alto%20-%20XDR%20%28Cortex%29/Data%20Connectors/Connector_PaloAlto_XDR_CEF.json) |

[→ View full connector details](../connectors/paloaltonetworkscortex.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Palo Alto Networks Cortex XDR](../connectors/paloaltonetworkscortex.md) |

[← Back to Solutions Index](../solutions-index.md)
