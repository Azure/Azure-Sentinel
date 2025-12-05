# CiscoUmbrella

## Solution Information

| | |
|------------------------|-------|
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

### [Cisco Cloud Security (using elastic premium plan)](../connectors/ciscoumbrelladataconnectorelasticpremium.md)

**Publisher:** Cisco

The Cisco Umbrella data connector provides the capability to ingest [Cisco Umbrella](https://docs.umbrella.com/) events stored in Amazon S3 into Microsoft Sentinel using the Amazon S3 REST API. Refer to [Cisco Umbrella log management documentation](https://docs.umbrella.com/deployment-umbrella/docs/log-management) for more information.



**NOTE:** This data connector uses the [Azure Functions Premium Plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan?tabs=portal) to enable secure ingestion capabilities and will incur additional costs. More pricing details are [here](https://azure.microsoft.com/pricing/details/functions/?msockid=2f4366822d836a7c2ac673462cfc6ba8#pricing).

| | |
|--------------------------|---|
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

[← Back to Solutions Index](../solutions-index.md)
