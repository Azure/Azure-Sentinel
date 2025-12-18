# Dynatrace Problems

| | |
|----------|-------|
| **Connector ID** | `DynatraceProblems` |
| **Publisher** | Dynatrace |
| **Tables Ingested** | [`DynatraceProblems_CL`](../tables-index.md#dynatraceproblems_cl) |
| **Used in Solutions** | [Dynatrace](../solutions/dynatrace.md) |
| **Connector Definition Files** | [Connector_Dynatrace_Problems.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_Problems.json) |

This connector uses the [Dynatrace Problem REST API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/problems-v2) to ingest problem events into Microsoft Sentinel Log Analytics

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Dynatrace tenant (ex. xyz.dynatrace.com)**: You need a valid Dynatrace Tenant, to learn more about the Dynatrace platform [Start your free trial](https://www.dynatrace.com/trial).
- **Dynatrace Access Token**: You need a Dynatrace Access Token, the token should have ***Read problems*** (problems.read) scope.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Dynatrace Problem Events to Microsoft Sentinel**

Follow [these instructions](https://docs.dynatrace.com/docs/shortlink/token#create-api-token) to generate an access token.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
