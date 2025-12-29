# Dynatrace Attacks

| | |
|----------|-------|
| **Connector ID** | `DynatraceAttacks` |
| **Publisher** | Dynatrace |
| **Tables Ingested** | [`DynatraceAttacks_CL`](../tables-index.md#dynatraceattacks_cl) |
| **Used in Solutions** | [Dynatrace](../solutions/dynatrace.md) |
| **Connector Definition Files** | [Connector_Dynatrace_Attacks.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Data%20Connectors/Connector_Dynatrace_Attacks.json) |

This connector uses the Dynatrace Attacks REST API to ingest detected attacks into Microsoft Sentinel Log Analytics

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Dynatrace tenant (ex. xyz.dynatrace.com)**: You need a valid Dynatrace tenant with [Application Security](https://www.dynatrace.com/platform/application-security/) enabled, learn more about the [Dynatrace platform](https://www.dynatrace.com/).
- **Dynatrace Access Token**: You need a Dynatrace Access Token, the token should have ***Read attacks*** (attacks.read) scope.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Dynatrace Attack Events to Microsoft Sentinel**

Configure and Enable Dynatrace [Application Security](https://www.dynatrace.com/platform/application-security/). 
 Follow [these instructions](https://docs.dynatrace.com/docs/shortlink/token#create-api-token) to generate an access token.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
