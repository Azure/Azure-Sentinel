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

This solution provides **3 data connector(s)**.

### [SecurityScorecard Factor](../connectors/securityscorecardfactorazurefunctions.md)

**Publisher:** SecurityScorecard

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) Factors data connector provides the ability for Sentinel to import SecurityScorecard factor ratings as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when factor scores change or drop. SecurityScorecard factor ratings are updated daily based on evidence collected across the web.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityScorecardFactor_CL` |
| **Connector Definition Files** | [SecurityScorecardFactor_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings/Data%20Connectors/SecurityScorecardFactor/SecurityScorecardFactor_API_FunctionApp.json) |

[→ View full connector details](../connectors/securityscorecardfactorazurefunctions.md)

### [SecurityScorecard Issue](../connectors/securityscorecardissueazurefunctions.md)

**Publisher:** SecurityScorecard

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) Issues data connector provides the ability for Sentinel to import SecurityScorecard issue data as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when new cybersecurity issues are discovered.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityScorecardIssues_CL` |
| **Connector Definition Files** | [SecurityScorecardIssue_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings/Data%20Connectors/SecurityScorecardIssue/SecurityScorecardIssue_API_FunctionApp.json) |

[→ View full connector details](../connectors/securityscorecardissueazurefunctions.md)

### [SecurityScorecard Cybersecurity Ratings](../connectors/securityscorecardratingsazurefunctions.md)

**Publisher:** SecurityScorecard

SecurityScorecard is the leader in cybersecurity risk ratings. The [SecurityScorecard](https://www.SecurityScorecard.com/) data connector provides the ability for Sentinel to import SecurityScorecard ratings as logs. SecurityScorecard provides ratings for over 12 million companies and domains using countless data points from across the internet. Maintain full awareness of any company's security posture and be able to receive timely updates when scores change or drop. SecurityScorecard ratings are updated daily based on evidence collected across the web.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `SecurityScorecardRatings_CL` |
| **Connector Definition Files** | [SecurityScorecardRatings_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityScorecard%20Cybersecurity%20Ratings/Data%20Connectors/SecurityScorecardRatings/SecurityScorecardRatings_API_FunctionApp.json) |

[→ View full connector details](../connectors/securityscorecardratingsazurefunctions.md)

## Tables Reference

This solution ingests data into **3 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityScorecardFactor_CL` | [SecurityScorecard Factor](../connectors/securityscorecardfactorazurefunctions.md) |
| `SecurityScorecardIssues_CL` | [SecurityScorecard Issue](../connectors/securityscorecardissueazurefunctions.md) |
| `SecurityScorecardRatings_CL` | [SecurityScorecard Cybersecurity Ratings](../connectors/securityscorecardratingsazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
