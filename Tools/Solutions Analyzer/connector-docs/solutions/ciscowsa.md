# CiscoWSA

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Cisco Web Security Appliance](../connectors/ciscowsa.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Cisco Web Security Appliance](../connectors/ciscowsa.md) | Analytics, Hunting, Workbooks |

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
| [Cisco WSA - Access to unwanted site](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAAccessToUnwantedSite.yaml) | High | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Internet access from public IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAPublicIPSource.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Multiple attempts to download unwanted file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAMultipleUnwantedFileTypes.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Multiple errors to URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAMultipleErrorsToUrl.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Multiple errors to resource from risky category](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAMultipleErrorsToUnwantedCategory.yaml) | Medium | InitialAccess, CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Multiple infected files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAMultipleInfectedFiles.yaml) | High | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Suspected protocol abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAProtocolAbuse.yaml) | Medium | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Unexpected URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAUnexpectedUrl.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Unexpected file type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAUnexpectedFileType.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Unexpected uploads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSADataExfiltration.yaml) | High | Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Unscannable file or scan error](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Analytic%20Rules/CiscoWSAUnscannableFile.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cisco WSA - Blocked files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSABlockedFiles.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Potentially risky resources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSAUrlSuspiciousResources.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Rare URL with error](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSAUrlRareErrorUrl.yaml) | InitialAccess, CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Rare aplications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSARareApplications.yaml) | CommandAndControl, Exfiltration | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Top URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSATopResources.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Top aplications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSATopApplications.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - URL shorteners](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSAUrlShortenerLinks.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Uncategorized URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSAUncategorizedResources.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - Uploaded files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSAUploadedFiles.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [Cisco WSA - User errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Hunting%20Queries/CiscoWSAUrlUsersWithErrors.yaml) | InitialAccess, CommandAndControl | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CiscoWSA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Workbooks/CiscoWSA.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoWSAEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoWSA/Parsers/CiscoWSAEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 19-12-2024                     | Removed Deprecated **Data connector**       |
| 3.0.1       | 24-07-2024                     | Deprecating data connectors                 |
| 3.0.0       | 16-08-2023                     | Optimize the **Parser** by replacing the legacy code that uses regex with a more efficient algorithm to reduce the time taken to parse data. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
