# PingFederate

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] PingFederate via Legacy Agent](../connectors/pingfederate.md)
- [[Deprecated] PingFederate via AMA](../connectors/pingfederateama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] PingFederate via AMA](../connectors/pingfederateama.md), [[Deprecated] PingFederate via Legacy Agent](../connectors/pingfederate.md) | Analytics, Hunting, Workbooks |

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
| [Ping Federate - Abnormal password reset attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateAbnormalPasswordResetsAttempts.yaml) | High | CredentialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Abnormal password resets for user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateMultiplePasswordResetsForUser.yaml) | High | InitialAccess, Persistence, PrivilegeEscalation | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Authentication from new IP.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateAuthFromNewSource.yaml) | Low | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Forbidden country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateForbiddenCountry.yaml) | High | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - New user SSO success login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateNewUserSSO.yaml) | Low | InitialAccess, Persistence | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - OAuth old version](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateOauthOld.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Password reset request from unexpected source IP address..](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederatePasswordRstReqUnexpectedSource.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - SAML old version](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateSamlOld.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Unexpected authentication URL.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateUnexpectedAuthUrl.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Unexpected country for user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateUnexpectedUserCountry.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Unusual mail domain.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Analytic%20Rules/PingFederateUnusualMailDomain.yaml) | Medium | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Ping Federate - Authentication URLs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateAuthUrls.yaml) | CredentialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Authentication from unusual sources](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateUnusualSources.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Failed Authentication](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateFailedAuthentications.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateNewUsers.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Password reset requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederatePasswordResetRequests.yaml) | InitialAccess, Persistence | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Rare source IP addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateRareSources.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Requests from unusual countries](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateUnusualCountry.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - SAML subjects](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateSAMLSubjects.yaml) | CredentialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Top source IP addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateTopSources.yaml) | InitialAccess | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |
| [Ping Federate - Users recently reseted password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Hunting%20Queries/PingFederateUsersPaswordsReset.yaml) | InitialAccess, Persistence | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [PingFederate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Workbooks/PingFederate.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PingFederateEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/PingFederate/Parsers/PingFederateEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 22-11-2024                     |    Removed Deprecated **Data Connectors**                           |
| 3.0.1 	  | 12-07-2024 					   |    Deprecated **Data Connector** 									|
| 3.0.0       | 04-09-2023                     |	Addition of new PingFederate AMA **Data Connector**             |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
