# Citrix Analytics for Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Citrix Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://www.citrix.com/support/](https://www.citrix.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Analytics%20for%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Analytics%20for%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CITRIX SECURITY ANALYTICS](../connectors/citrix.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CitrixAnalytics_indicatorEventDetails_CL`](../tables/citrixanalytics-indicatoreventdetails-cl.md) | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) | Workbooks |
| [`CitrixAnalytics_indicatorSummary_CL`](../tables/citrixanalytics-indicatorsummary-cl.md) | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) | Workbooks |
| [`CitrixAnalytics_riskScoreChange_CL`](../tables/citrixanalytics-riskscorechange-cl.md) | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) | Workbooks |
| [`CitrixAnalytics_userProfile_CL`](../tables/citrixanalytics-userprofile-cl.md) | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Citrix](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Analytics%20for%20Security/Workbooks/Citrix.json) | [`CitrixAnalytics_indicatorEventDetails_CL`](../tables/citrixanalytics-indicatoreventdetails-cl.md)<br>[`CitrixAnalytics_indicatorSummary_CL`](../tables/citrixanalytics-indicatorsummary-cl.md)<br>[`CitrixAnalytics_riskScoreChange_CL`](../tables/citrixanalytics-riskscorechange-cl.md)<br>[`CitrixAnalytics_userProfile_CL`](../tables/citrixanalytics-userprofile-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
