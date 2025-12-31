# Quokka

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Quokka |
| **Support Tier** | Partner |
| **Support Link** | [https://www.quokka.io/contact-us#customer-support](https://www.quokka.io/contact-us#customer-support) |
| **Categories** | domains |
| **First Published** | 2025-10-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [QscoutAppEventsConnector](../connectors/qscoutappeventsccfdefinition.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`QscoutAppEvents_CL`](../tables/qscoutappevents-cl.md) | [QscoutAppEventsConnector](../connectors/qscoutappeventsccfdefinition.md) | Analytics, Workbooks |

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 1 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Quokka - Malicious Results Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka/Analytic%20Rules/MaliciousResultsDetection.yaml) | Medium | InitialAccess, Execution, Persistence, PrivilegeEscalation, DefenseEvasion, CredentialAccess, Discovery, Collection, CommandAndControl, Impact | [`QscoutAppEvents_CL`](../tables/qscoutappevents-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [QscoutDashboards](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Quokka/Workbooks/QscoutDashboards.json) | [`QscoutAppEvents_CL`](../tables/qscoutappevents-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                                     |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------------------|
| 3.0.0       | 07-11-2025                     | Initial Solution Release for Quokka **CCF Data Connector** with an Analytic Rule and a Workbook        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
