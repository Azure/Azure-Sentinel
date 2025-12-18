# Dynatrace Audit Logs

| | |
|----------|-------|
| **Connector ID** | `DynatraceAuditLogs` |
| **Publisher** | Dynatrace |
| **Tables Ingested** | [`DynatraceAuditLogs_CL`](../tables-index.md#dynatraceauditlogs_cl) |
| **Used in Solutions** | [Dynatrace](../solutions/dynatrace.md) |
| **Connector Definition Files** | [Connector_Dynatrace_AuditLogs.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_AuditLogs.json) |

This connector uses the [Dynatrace Audit Logs REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/audit-logs) to ingest tenant audit logs into Microsoft Sentinel Log Analytics

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Dynatrace tenant (ex. xyz.dynatrace.com)**: You need a valid Dynatrace Tenant, to learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial).
- **Dynatrace Access Token**: You need a Dynatrace Access Token, the token should have ***Read audit logs*** (auditLogs.read) scope.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Dynatrace Audit Log Events to Microsoft Sentinel**

Enable Dynatrace Audit [Logging](https://docs.dynatrace.com/docs/shortlink/audit-logs#enable-audit-logging). 
 Follow [these instructions](https://docs.dynatrace.com/docs/shortlink/token#create-api-token) to generate an access token.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
