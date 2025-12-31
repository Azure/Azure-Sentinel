# Veritas NetBackup

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Veritas Technologies LLC |
| **Support Tier** | Partner |
| **Support Link** | [https://www.veritas.com/content/support/en_US/contact-us](https://www.veritas.com/content/support/en_US/contact-us) |
| **Categories** | domains |
| **First Published** | 2023-09-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veritas%20NetBackup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veritas%20NetBackup) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`NetBackupAlerts_CL`](../tables/netbackupalerts-cl.md) | Analytics |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Alarming number of anomalies generated in NetBackup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veritas%20NetBackup/Analytic%20Rules/NetBackup_many_Anomalies.yaml) | Medium | Discovery, CredentialAccess | [`NetBackupAlerts_CL`](../tables/netbackupalerts-cl.md) |
| [Multiple failed attempts of NetBackup login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veritas%20NetBackup/Analytic%20Rules/NetBackup_many_login_fail.yaml) | Medium | CredentialAccess, Discovery | [`NetBackupAlerts_CL`](../tables/netbackupalerts-cl.md) |

## Additional Documentation

> 📄 *Source: [Veritas NetBackup/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veritas NetBackup/README.md)*

**Veritas NetBackup and Microsoft Sentinel Integration Guide**	

The integration between Veritas NetBackup and Microsoft Sentinel empowers security operations teams by providing valuable insights from Veritas NetBackup Anomaly Detection and Malware Scanning engines directly into Microsoft Sentinel.  
These insights provide the following advantages to Security and IT ops:


- Identification of early indicators of compromise such as malware or data anomaly detection including spikes in new uncompressible data or change in deduplication ratio, files modifications during backups, etc. 

- Enhances capabilities for security operators to prioritize and expedite the investigation of potential security incidents with the help of insights from threats published by Veritas NetBackup.

- Enables NetBackup users to ingest alerts and other data into their Sentinel instance. With Analytic Rules, Sentinel can automatically create Sentinel incidents from incoming events.


Veritas NetBackup has developed a first-class, in-product integration with Microsoft Sentinel. Security insights will be pushed via NetBackup APIs directly into the Microsoft Sentinel workspace, eliminating any dependency on playbooks or the need to develop data connectors separately.  The threat hunting queries with enrich anomaly events from NetBackup helps during Ransomware analysis and helps incident prioritization when security administrators deal with several thousand security events. 


**Prerequisites**

Veritas NetBackup should be configured to send appropriate events to Microsoft Sentinel and must be running version 10.2 or higher.

Microsoft Sentinel and NetBackup should be configured to connect to API end points using an account with the relevant privileges necessary to perform the desired operations.

A workspace key and ID are required for NetBackup to connect to Sentinel. These are generated in Sentinel via its SIEM WebUI/API interface and stored and used by the NetBackup primary server.

**How NetBackup Sends Events to Microsoft Sentinel**

Veritas NetBackup sends events to SIEM platforms using Microsoft Sentinel as an example. A workspace key and ID are required for NetBackup to connect to Sentinel. These are generated in Microsoft Sentinel via its SIEM WebUI/API interface and stored and used by the NetBackup primary server. Once NetBackup connect to Microsoft Sentinel, NetBackup audits its own logs for the type(s) of alerts you ve configured for forwarding to Microsoft Sentinel. The selected alerts are then sent to Microsoft Sentinel as audit alert broadcast messages. Ref Figure 1


**Connecting Veritas NetBackup to Microsoft Sentinel**


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                               |
|-------------|--------------------------------|------------------------------------------------------------------|
|  3.0.0      |  13-11-2024                    | Initial version  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
