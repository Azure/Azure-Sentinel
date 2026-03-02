# BeyondTrust PM Cloud

| | |
|----------|-------|
| **Connector ID** | `BeyondTrustPMCloud` |
| **Publisher** | BeyondTrust |
| **Tables Ingested** | [`BeyondTrustPM_ActivityAudits_CL`](../tables-index.md#beyondtrustpm_activityaudits_cl), [`BeyondTrustPM_ClientEvents_CL`](../tables-index.md#beyondtrustpm_clientevents_cl) |
| **Used in Solutions** | [BeyondTrustPMCloud](../solutions/beyondtrustpmcloud.md) |
| **Connector Definition Files** | [BeyondTrustPMCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BeyondTrustPMCloud/Data%20Connectors/BeyondTrustPMCloud_API_FunctionApp.json) |

The BeyondTrust Privilege Management Cloud data connector provides the capability to ingest activity audit logs and client event logs from BeyondTrust PM Cloud into Microsoft Sentinel.



This connector uses Azure Functions to pull data from the BeyondTrust PM Cloud API and ingest it into custom Log Analytics tables.

[← Back to Connectors Index](../connectors-index.md)
