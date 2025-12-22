# Microsoft Copilot

| | |
|----------|-------|
| **Connector ID** | `MicrosoftCopilot` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CopilotActivity`](../tables-index.md#copilotactivity) |
| **Used in Solutions** | [Microsoft Copilot](../solutions/microsoft-copilot.md) |
| **Connector Definition Files** | [MicrosoftCopilot_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Copilot/Data%20Connectors/MicrosoftCopilot_ConnectorDefinition.json) |

The Microsoft Copilot logs connector in Microsoft Sentinel enables the seamless ingestion of Copilot-generated activity logs into Microsoft Sentinel for advanced threat detection, investigation, and response. It collects telemetry from Microsoft Copilot services - such as usage data, prompts and system responses - and ingests into Microsoft Sentinel, allowing security teams to monitor for misuse, detect anomalies, and maintain compliance with organizational policies.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Tenant Permissions**: 'Security Administrator' or 'Global Administrator' on the workspace's tenant.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Copilot audit logs to Microsoft Sentinel**

This connector uses the Office Management API to get your Microsoft Copilot audit logs. The logs will be stored and processed in your existing Microsoft Sentinel workspace. You can find the data in the **CopilotActivity** table.
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
