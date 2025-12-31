# SecurityThreatEssentialSolution

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-03-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **15 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) | Analytics |
| [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) | Analytics |
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | Analytics |
| [`AuditLogs`](../tables/auditlogs.md) | Analytics |
| [`AzureActivity`](../tables/azureactivity.md) | Analytics |
| [`BaseLogs`](../tables/baselogs.md) | Analytics |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Analytics |
| [`OfficeActivity`](../tables/officeactivity.md) | Analytics |
| [`SigninLogs`](../tables/signinlogs.md) | Hunting |
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | Analytics |
| [`VMConnection`](../tables/vmconnection.md) | Analytics |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | Analytics |
| [`W3CIISLog`](../tables/w3ciislog.md) | Analytics |
| [`barracuda_CL`](../tables/barracuda-cl.md) | Analytics |
| [`meraki_CL`](../tables/meraki-cl.md) | Analytics |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 7 |
| Hunting Queries | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Possible AiTM Phishing Attempt Against Microsoft Entra ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/PossibleAiTMPhishingAttemptAgainstAAD.yaml) | Medium | InitialAccess, DefenseEvasion, CredentialAccess | [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md) |
| [Threat Essentials - Mail redirect via ExO transport rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_Mail_redirect_via_ExO_transport_rule.yaml) | Medium | Collection, Exfiltration | [`OfficeActivity`](../tables/officeactivity.md) |
| [Threat Essentials - Mass Cloud resource deletions Time Series Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_TimeSeriesAnomaly_Mass_Cloud_Resource_Deletions.yaml) | Medium | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Threat Essentials - Multiple admin membership removals from newly created admin.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_MultipleAdmin_membership_removals_from_NewAdmin.yaml) | Medium | Impact | [`AuditLogs`](../tables/auditlogs.md) |
| [Threat Essentials - NRT User added to Microsoft Entra ID Privileged Groups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_NRT_UseraddedtoPrivilgedGroups.yaml) | Medium | Persistence, PrivilegeEscalation | [`AuditLogs`](../tables/auditlogs.md) |
| [Threat Essentials - Time series anomaly for data size transferred to public internet](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_TimeSeriesAnomaly-MultiVendor_DataExfiltration.yaml) | Medium | Exfiltration | [`BaseLogs`](../tables/baselogs.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`VMConnection`](../tables/vmconnection.md) |
| [Threat Essentials - User Assigned Privileged Role](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Analytic%20Rules/Threat_Essentials_UserAssignedPrivilegedRole.yaml) | High | Persistence | [`AuditLogs`](../tables/auditlogs.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Threat Essentials - Signins From VPS Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Hunting%20Queries/Signins-From-VPS-Providers.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md) |
| [Threat Essentials - Signins from Nord VPN Providers](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityThreatEssentialSolution/Hunting%20Queries/Signins-from-NordVPN-Providers.yaml) | InitialAccess | [`SigninLogs`](../tables/signinlogs.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.3       | 05-06-2024                     | Added missing AMA **Data Connector** reference in **Analytic Rule**       |
| 3.0.2       | 18-03-2024                     | Tagged for dependent solutions for deployment                             |
| 3.0.1       | 10-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.  |
| 3.0.0       | 06-07-2023                     | Updating **Analytic rule** query for KQL failure                          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
