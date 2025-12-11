# CTERA

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CTERA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ctera.com/](https://www.ctera.com/) |
| **Categories** | domains |
| **First Published** | 2024-07-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CTERA Syslog](../connectors/ctera.md)

**Publisher:** CTERA Networks Ltd

The CTERA Data Connector for Microsoft Sentinel offers monitoring and threat detection capabilities for your CTERA solution.

 It includes a workbook visualizing the sum of all operations per type, deletions, and denied access operations.

 It also provides analytic rules which detects ransomware incidents and alert you when a user is blocked due to suspicious ransomware activity.

 Additionally, it helps you identify critical patterns such as mass access denied events, mass deletions, and mass permission changes, enabling proactive threat management and response.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Step 1: Connect CTERA Platform to Syslog**

Set up your CTERA portal syslog connection and Edge-Filer Syslog connector

**2. Step 2: Install Azure Monitor Agent (AMA) on Syslog Server**

Install the Azure Monitor Agent (AMA) on your syslog server to enable data collection.

| | |
|--------------------------|---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [CTERA_Data_Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CTERA/Data%20Connectors/CTERA_Data_Connector.json) |

[→ View full connector details](../connectors/ctera.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [CTERA Syslog](../connectors/ctera.md) |

[← Back to Solutions Index](../solutions-index.md)
