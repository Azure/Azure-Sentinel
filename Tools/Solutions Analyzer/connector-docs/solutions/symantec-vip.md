# Symantec VIP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Symantec VIP](../connectors/symantecvip.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Symantec VIP](../connectors/symantecvip.md) | Analytics, Workbooks |

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
| [ClientDeniedAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP/Analytic%20Rules/ClientDeniedAccess.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [Excessive Failed Authentication from Invalid Inputs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP/Analytic%20Rules/ExcessiveFailedAuthenticationsfromInvalidInputs.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SymantecVIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP/Workbooks/SymantecVIP.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SymantecVIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Symantec%20VIP/Parsers/SymantecVIP.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                             |
|-------------|--------------------------------|------------------------------------------------|
| 3.0.2       | 20-01-2025                     | Removed Custom Entity mappings from **Analytic rules**          |
| 3.0.1       | 31-12-2024                     | Removed Deprecated **Data connector**          |
| 3.0.0       | 01-08-2024                     | Update **Parser** as part of Syslog migration  |
|             |                                | Deprecating data connectors                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
