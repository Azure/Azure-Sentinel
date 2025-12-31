# GDPR Compliance & Data Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-10-08 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **27 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AADUserRiskEvents`](../tables/aaduserriskevents.md) | Workbooks |
| [`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md) | Workbooks |
| [`AZFWApplicationRule`](../tables/azfwapplicationrule.md) | Workbooks |
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | Workbooks |
| [`AuditLogs`](../tables/auditlogs.md) | Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Workbooks |
| [`Correlate`](../tables/correlate.md) | Workbooks |
| [`IncidentNumber`](../tables/incidentnumber.md) | Workbooks |
| [`InitialDataSet`](../tables/initialdataset.md) | Workbooks |
| [`LAQueryLogs`](../tables/laquerylogs.md) | Workbooks |
| [`LogOns`](../tables/logons.md) | Workbooks |
| [`MicrosoftPurviewInformationProtection`](../tables/microsoftpurviewinformationprotection.md) | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | Workbooks |
| [`PurviewDataSensitivityLogs`](../tables/purviewdatasensitivitylogs.md) | Workbooks |
| [`RareAudits`](../tables/rareaudits.md) | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | Workbooks |
| [`Uncommon`](../tables/uncommon.md) | Workbooks |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | Workbooks |
| [`W3CIISLog`](../tables/w3ciislog.md) | Workbooks |
| [`aadFunc`](../tables/aadfunc.md) | Workbooks |
| [`auditLogEvents`](../tables/auditlogevents.md) | Workbooks |
| [`barracuda_CL`](../tables/barracuda-cl.md) | Workbooks |
| [`meraki_CL`](../tables/meraki-cl.md) | Workbooks |
| [`recentActivity`](../tables/recentactivity.md) | Workbooks |
| [`signIns`](../tables/signins.md) | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [GDPRComplianceAndDataSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/GDPR%20Compliance%20%26%20Data%20Security/Workbooks/GDPRComplianceAndDataSecurity.json) | [`AADUserRiskEvents`](../tables/aaduserriskevents.md)<br>[`ASimWebSessionLogs`](../tables/asimwebsessionlogs.md)<br>[`AZFWApplicationRule`](../tables/azfwapplicationrule.md)<br>[`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Correlate`](../tables/correlate.md)<br>[`IncidentNumber`](../tables/incidentnumber.md)<br>[`InitialDataSet`](../tables/initialdataset.md)<br>[`LAQueryLogs`](../tables/laquerylogs.md)<br>[`LogOns`](../tables/logons.md)<br>[`MicrosoftPurviewInformationProtection`](../tables/microsoftpurviewinformationprotection.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`PurviewDataSensitivityLogs`](../tables/purviewdatasensitivitylogs.md)<br>[`RareAudits`](../tables/rareaudits.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`SquidProxy_CL`](../tables/squidproxy-cl.md)<br>[`Uncommon`](../tables/uncommon.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`W3CIISLog`](../tables/w3ciislog.md)<br>[`aadFunc`](../tables/aadfunc.md)<br>[`auditLogEvents`](../tables/auditlogevents.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`recentActivity`](../tables/recentactivity.md)<br>[`signIns`](../tables/signins.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`SecurityAlert`](../tables/securityalert.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 								 |
|-------------|--------------------------------|-----------------------------------------------------------------------------------------------------| 
| 3.0.2       | 15-12-2025                     | Update the **Workbook** to include support for additional assets in the Watchlist.  	     |
| 3.0.1       | 18-11-2025                     | Fixing Issue with Defender Portal				     |
| 3.0.0       | 08-10-2025                     | Initial Solution Release						     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
