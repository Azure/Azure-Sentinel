# OSSEC

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] OSSEC via Legacy Agent](../connectors/ossec.md)

**Publisher:** OSSEC

OSSEC data connector provides the capability to ingest [OSSEC](https://www.ossec.net/) events into Microsoft Sentinel. Refer to [OSSEC documentation](https://www.ossec.net/docs) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_CEF_OSSEC.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC/Data%20Connectors/Connector_CEF_OSSEC.json) |

[→ View full connector details](../connectors/ossec.md)

### [[Deprecated] OSSEC via AMA](../connectors/ossecama.md)

**Publisher:** OSSEC

OSSEC data connector provides the capability to ingest [OSSEC](https://www.ossec.net/) events into Microsoft Sentinel. Refer to [OSSEC documentation](https://www.ossec.net/docs) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_OSSECAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OSSEC/Data%20Connectors/template_OSSECAMA.json) |

[→ View full connector details](../connectors/ossecama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] OSSEC via AMA](../connectors/ossecama.md), [[Deprecated] OSSEC via Legacy Agent](../connectors/ossec.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 21-11-2024                     | Removed Deprecated **Data Connectors**                             |
| 3.0.1 	  | 12-07-2024 					   | Deprecated **Data Connector** 										|
| 3.0.0       | 28-08-2023                     | Addition of new OSSEC AMA **Data Connector**                    	|

[← Back to Solutions Index](../solutions-index.md)
