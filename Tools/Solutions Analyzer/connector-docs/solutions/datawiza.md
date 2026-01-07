# Datawiza

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Datawiza Technology Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://www.datawiza.com/contact-us/](https://www.datawiza.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-11-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datawiza](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datawiza) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Datawiza DAP](../connectors/datawizadapsolution.md)

**Publisher:** Datawiza

Connects the Datawiza DAP logs to Azure Log Analytics via the REST API interface

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Step 1 : Read the detailed documentation**

The installation process is documented in great detail in the documentation site [Microsoft Sentinel integration](https://docs.datawiza.com/tutorial/integrate-with-microsoft-sentinel.html). The user should consult our support (support@datawiza.com) further to understand installation and debug of the integration.

**2. Step 2: Install the Datawiza Sentinel Connector**

The next step is to install the Datawiza log forwarder to send logs to Microsoft Sentinel. The exact installation will depend on your environment, consult the [Microsoft Sentinel integration](https://docs.datawiza.com/tutorial/integrate-with-microsoft-sentinel.html) for full details.

**3. Step 3: Test the data ingestion**

After approximately 20 minutes access the Log Analytics workspace on your Microsoft Sentinel installation, and locate the *Custom Logs* section verify that a *datawizaserveraccess_CL* table exists. Use the sample queries to examine the data.

| | |
|--------------------------|---|
| **Tables Ingested** | `datawizaserveraccess_CL` |
| **Connector Definition Files** | [Datawiza_DAP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Datawiza/Data%20Connectors/Datawiza_DAP.json) |

[→ View full connector details](../connectors/datawizadapsolution.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `datawizaserveraccess_CL` | [Datawiza DAP](../connectors/datawizadapsolution.md) |

[← Back to Solutions Index](../solutions-index.md)
