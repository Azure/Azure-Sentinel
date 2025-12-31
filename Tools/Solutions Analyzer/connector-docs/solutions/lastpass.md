# LastPass

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | The Collective Consulting |
| **Support Tier** | Partner |
| **Support Link** | [https://thecollective.eu](https://thecollective.eu) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Last Updated** | 2022-01-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [LastPass Enterprise - Reporting (Polling CCP)](../connectors/lastpass-polling.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md) | [LastPass Enterprise - Reporting (Polling CCP)](../connectors/lastpass-polling.md) | Analytics, Hunting, Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | - | Hunting, Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Analytics |

## Content Items

This solution includes **10 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Hunting Queries | 3 |
| Workbooks | 1 |
| Watchlists | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Employee account deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Analytic%20Rules/EmployeeAccountDeleted.yaml) | Medium | Impact | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md) |
| [Failed sign-ins into LastPass due to MFA](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Analytic%20Rules/FailedSigninDueToMFA.yaml) | Low | InitialAccess | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md) |
| [Highly Sensitive Password Accessed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Analytic%20Rules/HighlySensitivePasswordAccessed.yaml) | Medium | CredentialAccess, Discovery | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md) |
| [TI map IP entity to LastPass data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Analytic%20Rules/TIMapIPEntityToLastPass.yaml) | Medium | Impact | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) |
| [Unusual Volume of Password Updated or Removed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Analytic%20Rules/UnusualVolumeOfPasswordsUpdatedOrRemoved.yaml) | Low | Impact | - |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Failed sign-ins into LastPass due to MFA.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Hunting%20Queries/FailedSigninsDueToMFA.yaml) | InitialAccess | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md) |
| [Login into LastPass from a previously unknown IP.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Hunting%20Queries/LoginIntoLastPassFromUnknownIP.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Password moved to shared folders](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Hunting%20Queries/PasswordMoveToSharedFolder.yaml) | Collection | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [LastPassWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Workbooks/LastPassWorkbook.json) | [`LastPassNativePoller_CL`](../tables/lastpassnativepoller-cl.md)<br>[`SigninLogs`](../tables/signinlogs.md) |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [HighlySensitivePasswords](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Watchlists/HighlySensitivePasswords.json) | - | - |

## Additional Documentation

> 📄 *Source: [LastPass/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/README.md)*

This repository contains all resources for the LastPass Microsoft Sentinel Solution.
The LastPass Solution is built in order to easily integrate LastPass with Microsoft Sentinel.

By deploying this solution, you'll be able to monitor activity within LastPass and be alerted when potential security events arise.
The solution consists out of the following resources:
- A codeless API connector to ingest data into Sentinel.
- One workbook to visualize some of the activity within LastPass
- Hunting Queries to look into potential security events
- Analytic Rules to generate alerts and incidents when potential malicious events happen

## Data Connector Deployment
The data connector will retrieve the LastPass Activity data through the LastPass Enterprise API.

Authentication is done through a LastPass Provisioning Hash API key which can be generated by a LastPass administrator by following the steps in the following [How To Article](https://support.logmeininc.com/lastpass/help/use-the-lastpass-provisioning-api-lp010068).

This is a codeless API connector. After the deployment of the ARM template, the connector will be available in the list to connect.
Input the API key and Microsoft Sentinel will start to pull in data.

## Workbook
The workbook contains visualizations about the activity within LastPass and provides an overview of the user activity.
This allows you to identify user with a high amount of activity.

Besides user activity, the sign-ins logs are correlated to point out sign-ins which were done from previously unknown IPs and admin activity is surfaced.

The workbook can be deployed by creating an empty workbook and adding the data from the Gallery template.

## Hunting
- Login into LastPass from a previously unknown IP.
- Failed sign-ins into LastPass due to MFA.
- Password moved to shared folders

## Analytic Rules
The solution currently includes five analytic rules:
- TI map IP entity to LastPass data
- Highly Sensitive Password Accessed
- Failed sign-ins into LastPass due to MFA
- Employee account deleted
- Unusual Volume of Password Updated or Removed

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.0       | 07-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
