# GoogleCloudPlatformDNS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-07-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md)
- [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`GCPDNS`](../tables/gcpdns.md) | [Google Cloud Platform DNS (via Codeless Connector Framework)](../connectors/gcpdnslogsccpdefinition.md) | - |
| [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) | [[DEPRECATED] Google Cloud Platform DNS](../connectors/gcpdnsdataconnector.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 11 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Google DNS - CVE-2020-1350 (SIGRED) exploitation pattern](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSSIGREDPattern.yaml) | High | PrivilegeEscalation | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - CVE-2021-34527 (PrintNightmare) external exploit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSPrintNightmare.yaml) | High | PrivilegeEscalation | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - CVE-2021-40444 exploitation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSCVE-2021-40444.yaml) | High | PrivilegeEscalation | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Exchange online autodiscover abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSExchangeAutodiscoverAbuse.yaml) | Medium | InitialAccess, CredentialAccess | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - IP check activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSIpCheck.yaml) | Medium | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Malicous Python packages](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSMaliciousPythonPackages.yaml) | High | InitialAccess | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Multiple errors for source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSMultipleErrorsFromIp.yaml) | Medium | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Multiple errors to same domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSMultipleErrorsQuery.yaml) | Medium | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Possible data exfiltration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSDataExfiltration.yaml) | High | Exfiltration | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Request to dynamic DNS service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSIpDynDns.yaml) | Medium | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - UNC2452 (Nobelium) APT Group activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Analytic%20Rules/GCPDNSUNC2452AptActivity.yaml) | High | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Google DNS - Domains with rare errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSRareErrors.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSErrors.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Rare domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSRareDomains.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Requests to IP lookup resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSIpLookup.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Requests to TOR resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSRequestToTOR.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Requests to online shares](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSOnlineShares.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Server latency](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSServerLatency.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Sources with high number of errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSSourceHighErrors.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Unexpected top level domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSUnexpectedTLD.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |
| [Google DNS - Unusual top level domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Hunting%20Queries/GCPDNSUnusualTLD.yaml) | CommandAndControl | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [GCPDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Workbooks/GCPDNS.json) | [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [GCPCloudDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GoogleCloudPlatformDNS/Parsers/GCPCloudDNS.yaml) | - | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)**| **ChangeHistory**                                                                         |
|------------|-------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.5      | 29-07-2025                    | Removed Deprecated **Data Connector**. | 
| 3.0.4      | 26-06-2025                    | Moving **CCF Connector** - *Google Cloud Platform DNS* from Public preview to GA.         |
| 3.0.3      | 09-05-2025                    | Implemented Standard table Functionality to **CCF Connector** - *Google Cloud Platform DNS*.   |
| 3.0.2      | 11-02-2025                    | Migrated the **Function app** connector to CCP **Data Connctor** and Updated **Parser**.   |
| 3.0.1      | 10-09-2024                    | Repackaged solution to add existing **Parser**.                                            |
| 3.0.0      | 04-09-2024                    | Updated the python runtime version to 3.11 Function app **Data Connector**.                      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
