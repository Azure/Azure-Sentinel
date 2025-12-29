# CiscoUmbrella

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-04-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md)

**Publisher:** Cisco

The Cisco Cloud Security solution for Microsoft Sentinel enables you to ingest [Cisco Secure Access](https://docs.sse.cisco.com/sse-user-guide/docs/welcome-cisco-secure-access) and [Cisco Umbrella](https://docs.umbrella.com/umbrella-user-guide/docs/getting-started) [logs](https://docs.sse.cisco.com/sse-user-guide/docs/manage-your-logs) stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Cloud Security log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Cisco_Umbrella_audit_CL` |
| | `Cisco_Umbrella_cloudfirewall_CL` |
| | `Cisco_Umbrella_dlp_CL` |
| | `Cisco_Umbrella_dns_CL` |
| | `Cisco_Umbrella_fileevent_CL` |
| | `Cisco_Umbrella_firewall_CL` |
| | `Cisco_Umbrella_intrusion_CL` |
| | `Cisco_Umbrella_ip_CL` |
| | `Cisco_Umbrella_proxy_CL` |
| | `Cisco_Umbrella_ravpnlogs_CL` |
| | `Cisco_Umbrella_ztaflow_CL` |
| | `Cisco_Umbrella_ztna_CL` |
| **Connector Definition Files** | [CiscoUmbrella_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Data%20Connectors/CiscoUmbrella_API_FunctionApp.json) |

[→ View full connector details](../connectors/ciscoumbrelladataconnector.md)

### [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md)

**Publisher:** Cisco

The Cisco Umbrella data connector provides the capability to ingest [Cisco Umbrella](https://docs.umbrella.com/) events stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Umbrella log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.



**NOTE:** This data connector uses the [Azure Functions Premium Plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan?tabs=portal) to enable secure ingestion capabilities and will incur additional costs. More pricing details are [here](https://azure.microsoft.com/pricing/details/functions/?msockid=2f4366822d836a7c2ac673462cfc6ba8#pricing).

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Cisco_Umbrella_audit_CL` |
| | `Cisco_Umbrella_cloudfirewall_CL` |
| | `Cisco_Umbrella_dlp_CL` |
| | `Cisco_Umbrella_dns_CL` |
| | `Cisco_Umbrella_fileevent_CL` |
| | `Cisco_Umbrella_firewall_CL` |
| | `Cisco_Umbrella_intrusion_CL` |
| | `Cisco_Umbrella_ip_CL` |
| | `Cisco_Umbrella_proxy_CL` |
| | `Cisco_Umbrella_ravpnlogs_CL` |
| | `Cisco_Umbrella_ztaflow_CL` |
| | `Cisco_Umbrella_ztna_CL` |
| **Connector Definition Files** | [CiscoUmbrella_API_FunctionApp_elasticpremium.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoUmbrella/Data%20Connectors/CiscoUmbrella_API_FunctionApp_elasticpremium.json) |

[→ View full connector details](../connectors/ciscoumbrelladataconnectorelasticpremium.md)

## Tables Reference

This solution ingests data into **12 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Cisco_Umbrella_audit_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_cloudfirewall_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_dlp_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_dns_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_fileevent_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_firewall_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_intrusion_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_ip_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_proxy_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_ravpnlogs_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_ztaflow_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |
| `Cisco_Umbrella_ztna_CL` | [Cisco Cloud Security](../connectors/ciscoumbrelladataconnector.md), [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.7       | 28-11-2025                     | The Data connector has been updated to support up to version 14 log versioning for the Cisco log format, and the parser to include all tables. |
| 3.0.6       | 01-09-2025                     | Added a new data connector, 'CiscoUmbrella_API_FunctionApp_elasticpremium.json'    |
| 3.0.5       | 21-06-2025                     | To expand support for Cisco Umbrella data in KQL validation tests and to standardize the naming of analytic rules    |
| 3.0.4       | 15-05-2025                     | Updating documentation to reflect support for Cisco Umbrella log schema version 11    |
| 3.0.3       | 30-12-2024                     | Update Playbooks **AddIpToDestination**, **AssignPolicyToIdentity**, **GetDomainInfo** as v1 version of CiscoUmbrella APIs are deprecated and Urls are also changed for this. **Cisco Umbrella Enforcement API has not been deprecated**. Repackage of solution.    |
| 3.0.2       | 20-09-2024                     | Update **Analytic rules** for Entity mapping and missing TTP and Updated the python runtime version to 3.11    |
| 3.0.1       | 03-05-2024                     | Added Deploy to Azure Government button in **Data connector** <br/> Fixed **Parser** issue for Parser name and ParentID mismatch|
| 3.0.0       | 28-09-2023                     | Updated **Data Connector** with step by step guidelines |

[← Back to Solutions Index](../solutions-index.md)
