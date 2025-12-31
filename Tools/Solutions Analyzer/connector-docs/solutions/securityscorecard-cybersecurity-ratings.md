# SecurityScorecard Cybersecurity Ratings

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SecurityScorecard |
| **Support Tier** | Partner |
| **Support Link** | [https://support.securityscorecard.com/hc/en-us/requests/new](https://support.securityscorecard.com/hc/en-us/requests/new) |
| **Categories** | domains |
| **First Published** | 2022-10-01 |
| **Last Updated** | 2022-10-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [SecurityScorecard Factor](../connectors/securityscorecardfactorazurefunctions.md)
- [SecurityScorecard Issue](../connectors/securityscorecardissueazurefunctions.md)
- [SecurityScorecard Cybersecurity Ratings](../connectors/securityscorecardratingsazurefunctions.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityScorecardFactor_CL`](../tables/securityscorecardfactor-cl.md) | [SecurityScorecard Factor](../connectors/securityscorecardfactorazurefunctions.md) | Workbooks |
| [`SecurityScorecardIssues_CL`](../tables/securityscorecardissues-cl.md) | [SecurityScorecard Issue](../connectors/securityscorecardissueazurefunctions.md) | Workbooks |
| [`SecurityScorecardRatings_CL`](../tables/securityscorecardratings-cl.md) | [SecurityScorecard Cybersecurity Ratings](../connectors/securityscorecardratingsazurefunctions.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SecurityScorecardWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings/Workbooks/SecurityScorecardWorkbook.json) | [`SecurityScorecardFactor_CL`](../tables/securityscorecardfactor-cl.md)<br>[`SecurityScorecardIssues_CL`](../tables/securityscorecardissues-cl.md)<br>[`SecurityScorecardRatings_CL`](../tables/securityscorecardratings-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
