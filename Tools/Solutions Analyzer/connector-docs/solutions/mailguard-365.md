# MailGuard 365

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | MailGuard 365 |
| **Support Tier** | Partner |
| **Support Link** | [https://www.mailguard365.com/support/](https://www.mailguard365.com/support/) |
| **Categories** | domains |
| **First Published** | 2023-05-09 |
| **Last Updated** | 2023-06-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [MailGuard 365](../connectors/mailguard365.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`MailGuard365_Threats_CL`](../tables/mailguard365-threats-cl.md) | [MailGuard 365](../connectors/mailguard365.md) | Hunting, Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 3 |
| Workbooks | 1 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [MailGuard 365 - High Confidence Threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365/Hunting%20Queries/MailGuard365HighConfidenceThreats.yaml) | Reconnaissance | [`MailGuard365_Threats_CL`](../tables/mailguard365-threats-cl.md) |
| [MailGuard 365 - Malware Threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365/Hunting%20Queries/MailGuard365MalwareThreats.yaml) | InitialAccess, Reconnaissance | [`MailGuard365_Threats_CL`](../tables/mailguard365-threats-cl.md) |
| [MailGuard 365 - Phishing Threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365/Hunting%20Queries/MailGuard365PhishingThreats.yaml) | InitialAccess, Reconnaissance, Credential Access | [`MailGuard365_Threats_CL`](../tables/mailguard365-threats-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MailGuard365Dashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailGuard%20365/Workbooks/MailGuard365Dashboard.json) | [`MailGuard365_Threats_CL`](../tables/mailguard365-threats-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 31-08-2023                     | Initial Solution Release                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
