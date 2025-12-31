# Digital Guardian Data Loss Prevention

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Digital Guardian Data Loss Prevention](../connectors/digitalguardiandlp.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Digital Guardian Data Loss Prevention](../connectors/digitalguardiandlp.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Digital Guardian - Bulk exfiltration to external domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianFilesSentToExternalDomain.yaml) | Medium | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Exfiltration to external domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianFileSentToExternalDomain.yaml) | Medium | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Exfiltration to online fileshare](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianExfiltrationToFileShareServices.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Exfiltration to private email](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianFileSentToExternal.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Exfiltration using DNS protocol](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianExfiltrationOverDNS.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Incident with not blocked action](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianViolationNotBlocked.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Multiple incidents from user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianMultipleIncidentsFromUser.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Possible SMTP protocol abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianPossibleProtocolAbuse.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Sensitive data transfer over insecure channel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianClassifiedDataInsecureTransfer.yaml) | Medium | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Unexpected protocol](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Analytic%20Rules/DigitalGuardianUnexpectedProtocol.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Digital Guardian - Files sent by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianFilesSentByUsers.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Incident domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianDomains.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Insecure file transfer sources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianInsecureProtocolSources.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Inspected files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianInspectedFiles.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - New incidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianNewIncidents.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Rare Urls](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianRareUrls.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Rare destination ports](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianRareDestinationPorts.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Rare network protocols](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianRareNetworkProtocols.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Urls used](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianUrlByUser.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Digital Guardian - Users' incidents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Hunting%20Queries/DigitalGuardianIncidentsByUser.yaml) | Exfiltration | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DigitalGuardian](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Workbooks/DigitalGuardian.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DigitalGuardianDLPEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Guardian%20Data%20Loss%20Prevention/Parsers/DigitalGuardianDLPEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                        |
|-------------|--------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.2       | 26-12-2024                     | Removed Deprecated **Data connector**                                                     |
| 3.0.1       | 25-07-2024                     | Deprecating data connectors                                                               |
| 3.0.0       | 09-10-2023                     | Fixed KQL validation failure in **Hunting Query** (Digital Guardian - Users incidents)    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
