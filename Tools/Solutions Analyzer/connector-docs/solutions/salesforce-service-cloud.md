# Salesforce Service Cloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md)
- [Salesforce Service Cloud (via Codeless Connector Framework)](../connectors/salesforceservicecloudccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SalesforceServiceCloudV2_CL`](../tables/salesforceservicecloudv2-cl.md) | [Salesforce Service Cloud (via Codeless Connector Framework)](../connectors/salesforceservicecloudccpdefinition.md), [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md) | Analytics, Workbooks |
| [`SalesforceServiceCloud_CL`](../tables/salesforceservicecloud-cl.md) | [[DEPRECATED] Salesforce Service Cloud](../connectors/salesforceservicecloud.md) | Analytics, Workbooks |
| [`ThreatIntelIndicatorsv2`](../tables/threatintelindicatorsv2.md) | - | Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Brute force attack against user credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Analytic%20Rules/Salesforce-BruteForce.yaml) | Medium | CredentialAccess | [`SalesforceServiceCloudV2_CL`](../tables/salesforceservicecloudv2-cl.md)<br>[`SalesforceServiceCloud_CL`](../tables/salesforceservicecloud-cl.md) |
| [Potential Password Spray Attack](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Analytic%20Rules/Salesforce-PasswordSpray.yaml) | Medium | CredentialAccess | [`SalesforceServiceCloudV2_CL`](../tables/salesforceservicecloudv2-cl.md)<br>[`SalesforceServiceCloud_CL`](../tables/salesforceservicecloud-cl.md) |
| [User Sign in from different countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Analytic%20Rules/Salesforce-SigninsMultipleCountries.yaml) | Medium | InitialAccess | [`SalesforceServiceCloudV2_CL`](../tables/salesforceservicecloudv2-cl.md)<br>[`SalesforceServiceCloud_CL`](../tables/salesforceservicecloud-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SalesforceServiceCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Workbooks/SalesforceServiceCloud.json) | [`SalesforceServiceCloudV2_CL`](../tables/salesforceservicecloudv2-cl.md)<br>[`SalesforceServiceCloud_CL`](../tables/salesforceservicecloud-cl.md)<br>[`ThreatIntelIndicatorsv2`](../tables/threatintelindicatorsv2.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SalesforceServiceCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Salesforce%20Service%20Cloud/Parsers/SalesforceServiceCloud.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.9       | 17-11-2025                     | Resolved bug in **CCF Data Connector** related to column names     |
| 3.0.8       | 04-11-2025                     | Resolved bugs in **Analytic rules** related to TimestampDerived field.         |
| 3.0.7       | 02-11-2025                     | Updated CCF Data Connector polling config to v65.0.                |
| 3.0.6       | 17-10-2025                     | Updated KQL transformation logic to map USER_NAME to the UserEmail column instead of USER_EMAIL.|
| 3.0.5       | 20-08-2025                     | Moving Salesforce Service cloud **CCF Data Connector** to GA.		|
| 3.0.4       | 11-07-2025                     | Salesforce **Workbook** updated with new ThreatIntelIndicators.	|
| 3.0.3       | 03-07-2025                     | Added Preview tag to CCF Connector title.<br/>Deprecated Function app Connector.		|
| 3.0.2       | 24-03-2025                     | Updated **Analytic rules** query to use TimeStampDerived column rather than TimeGenerated. |
| 3.0.1       | 06-02-2025                     | Updated timeframes for Salesforce cloud **Analytic rules**.			|
| 3.0.0       | 05-09-2023                     | Manual deployment instructions updated for **Data Connector**.		|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
