# Authomize

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Authomize |
| **Support Tier** | Partner |
| **Support Link** | [https://support.authomize.com](https://support.authomize.com) |
| **Categories** | domains,verticals |
| **First Published** | 2023-06-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Authomize Data Connector](../connectors/authomize.md)

**Publisher:** Authomize

The Authomize Data Connector provides the capability to ingest custom log types from Authomize into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Include custom pre-requisites if the connectivity requires - else delete customs**: Description for any custom pre-requisite

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Locate your Authomize API key**

Follow the setup instructions [located under Data Connectors for Authomize](https://github.com/authomize/Open-ITDR/blob/main/Open-Connectors/Platform/Azure-Sentinel/Data%20Connectors/readme.md).

**2. Deploy the Authomize data connector using the setup instructions.**

Follow the Instructions on [deploying the data connector to ingest data from Authomize](https://github.com/authomize/Open-ITDR/blob/main/Open-Connectors/Platform/Azure-Sentinel/Data%20Connectors/readme.md).

**3. Finalize your setup**

Validate that your script is running. Simple instructions are located under the [Authomize Data Connector area](https://github.com/authomize/Open-ITDR/blob/main/Open-Connectors/Platform/Azure-Sentinel/Data%20Connectors/readme.md).

| | |
|--------------------------|---|
| **Tables Ingested** | `Authomize_v2_CL` |
| **Connector Definition Files** | [AuthomizeCustomConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Authomize/Data%20Connectors/AuthomizeCustomConnector.json) |

[→ View full connector details](../connectors/authomize.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Authomize_v2_CL` | [Authomize Data Connector](../connectors/authomize.md) |

[← Back to Solutions Index](../solutions-index.md)
