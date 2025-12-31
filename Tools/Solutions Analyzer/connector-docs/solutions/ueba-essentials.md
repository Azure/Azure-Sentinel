# UEBA Essentials

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **2 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AuditLogs`](../tables/auditlogs.md) | Hunting |
| [`SigninLogs`](../tables/signinlogs.md) | Hunting |

### Internal Tables

The following **3 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`Anomalies`](../tables/anomalies.md) | Hunting |
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Hunting |
| [`IdentityInfo`](../tables/identityinfo.md) | Hunting |

## Content Items

This solution includes **30 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Hunting Queries | 30 |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Anomalies on users tagged as VIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/anomaliesOnVIPUsers.yaml) | - | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous AWS Console Login Without MFA from Uncommon Country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20AWS%20Console%20Login%20Without%20MFA%20from%20Uncommon%20Country.yaml) | InitialAccess, CredentialAccess | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Activity Role Assignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Activity%20Role%20Assignment.yaml) | PrivilegeEscalation | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Code Execution on a Virtual Machine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Code%20Execution.yaml) | Execution | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Database Export Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Database%20Export%20Activity.yaml) | Collection | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Database Vulnerability Baseline Removal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Database%20Vulnerability%20Baseline%20Removal.yaml) | DefenseEvasion | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Entra High-Privilege Role Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Entra%20High-Privilege%20Role%20Modification.yaml) | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [Anomalous Failed Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Failed%20Logon.yaml) | CredentialAccess | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous First-Time Device Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20First-Time%20Device%20Logon.yaml) | InitialAccess, LateralMovement | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous GCP IAM Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20GCP%20IAM%20Activity.yaml) | PrivilegeEscalation, Persistence, CredentialAccess | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Geo Location Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Geo%20Location%20Logon.yaml) | InitialAccess | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous High-Privileged Role Assignment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20High-Privileged%20Role%20Assignment.yaml) | Persistence | [`AuditLogs`](../tables/auditlogs.md) |
| [Anomalous High-Score Activity Triage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20High-Score%20Activity%20Triage.yaml) | - | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md) |
| [Anomalous Key Vault Modification by High-Privilege User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/updateKeyVaultActivity.yaml) | - | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Microsoft Entra ID Account Creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Account%20Creation.yaml) | Persistence | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Okta First-Time or Uncommon Actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Okta%20First-Time%20or%20Uncommon%20Actions.yaml) | InitialAccess, CredentialAccess, Persistence | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Password Reset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Password%20Reset.yaml) | Impact | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous RDP Activity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20RDP%20Activity.yaml) | LateralMovement | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Resource Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Resource%20Access.yaml) | LateralMovement | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous Sign-in by New or Dormant Account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20Sign-in%20Activity.yaml) | Persistence | [`SigninLogs`](../tables/signinlogs.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous action performed in tenant by privileged user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/anomalousActionInTenant.yaml) | - | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomalous connection from highly privileged user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomalous%20connection%20from%20highly%20privileged%20user.yaml) | - | *Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md) |
| [Anomalous login activity originated from Botnet, Tor proxy or C2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/loginActivityFromBotnet.yaml) | - | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Anomaly Detection Trend Analysis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomaly%20Detection%20Trend%20Analysis.yaml) | - | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md) |
| [Anomaly Template Distribution by Tactics and Techniques](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Anomaly%20Template%20Distribution%20by%20Tactics%20and%20Techniques.yaml) | - | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md) |
| [Dormant Local Admin Logon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Dormant%20Local%20Admin%20Logon.yaml) | PrivilegeEscalation | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Dormant account activity from uncommon country](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/dormantAccountActivityFromUncommonCountry.yaml) | - | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Top Anomalous Source IP Triage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/Top%20Anomalous%20Source%20IP%20Triage.yaml) | - | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md) |
| [UEBA Multi-Source Anomalous Activity Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/UEBA%20Multi-Source%20Anomalous%20Activity%20Overview.yaml) | InitialAccess, CredentialAccess, Persistence, PrivilegeEscalation | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md) |
| [User-Centric Anomaly Investigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/UEBA%20Essentials/Hunting%20Queries/User-Centric%20Anomaly%20Investigation.yaml) | - | *Internal use:*<br>[`Anomalies`](../tables/anomalies.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                        |
|-------------|--------------------------------|-------------------------------------------------------------------------------------------|
| 3.0.3       | 24-11-2025                     | Added new **Hunting Queries**                                          	               |
| 3.0.2       | 04-11-2025                     | Enhance UEBA Essentials with multi-cloud detection capabilities        	               |
| 3.0.1       | 23-09-2024                     | Updated query logic in **Hunting Query** [Anomalous Sign-in Activity]                     |
| 3.0.0       | 07-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.   |
| 4.1.0       | 23-11-2025                     | Added new hunting queries: User-Centric Anomaly Investigation, Anomaly Detection Trend Analysis, Anomaly Template Distribution, Anomalous High-Score Activity Triage, Top Anomalous Source IP Triage. Updated solution version. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
