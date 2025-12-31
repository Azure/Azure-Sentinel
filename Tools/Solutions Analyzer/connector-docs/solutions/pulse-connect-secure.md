# Pulse Connect Secure

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Pulse Connect Secure](../connectors/pulseconnectsecure.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Pulse Connect Secure](../connectors/pulseconnectsecure.md) | Analytics, Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [PulseConnectSecure - Large Number of Distinct Failed User Logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure/Analytic%20Rules/PulseConnectSecureVPN-DistinctFailedUserLogin.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [PulseConnectSecure - Potential Brute Force Attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure/Analytic%20Rules/PulseConnectSecureVPN-BruteForce.yaml) | Low | CredentialAccess | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PulseConnectSecure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure/Workbooks/PulseConnectSecure.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PulseConnectSecure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pulse%20Connect%20Secure/Parsers/PulseConnectSecure.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                  |
|-------------|--------------------------------|-----------------------------------------------------|
| 3.0.4       | 07-01-2025                     | Removed Custom Entity mappings from **Analytic Rule**     |
| 3.0.3       | 16-12-2024                     | Removed Deprecated **Data Connector**               |
| 3.0.2       | 01-08-2024                     | Update **Parser** as part of Syslog migration       |
|             |                                | Deprecating data connectors                         |
| 3.0.1       | 13-12-2023                     | Updated  broken link in **Data Connector**          |
| 3.0.0       | 20-07-2023                     | Corrected the links in the solution.                |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
