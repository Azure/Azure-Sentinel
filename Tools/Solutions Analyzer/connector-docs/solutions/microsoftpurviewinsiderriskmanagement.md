# MicrosoftPurviewInsiderRiskManagement

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft 365 Insider Risk Management](../connectors/officeirm.md)

## Tables Reference

This solution uses **23 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AADUserRiskEvents`](../tables/aaduserriskevents.md) | - | Workbooks |
| [`AuditLogs`](../tables/auditlogs.md) | - | Workbooks |
| [`AzureActivity`](../tables/azureactivity.md) | - | Hunting, Workbooks |
| [`Correlate`](../tables/correlate.md) | - | Workbooks |
| [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) | - | Analytics |
| [`InitialDataSet`](../tables/initialdataset.md) | - | Workbooks |
| [`LAQueryLogs`](../tables/laquerylogs.md) | - | Workbooks |
| [`LogOns`](../tables/logons.md) | - | Workbooks |
| [`MicrosoftPurviewInformationProtection`](../tables/microsoftpurviewinformationprotection.md) | - | Workbooks |
| [`NewUserAddsUser`](../tables/newuseraddsuser.md) | - | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | - | Workbooks |
| [`PasswordResetMultiDataSource`](../tables/passwordresetmultidatasource.md) | - | Workbooks |
| [`RareAudits`](../tables/rareaudits.md) | - | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | - | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | - | Analytics, Hunting, Workbooks |
| [`Uncommon`](../tables/uncommon.md) | - | Hunting, Workbooks |
| [`UserAddWithResource`](../tables/useraddwithresource.md) | - | Workbooks |
| [`aadFunc`](../tables/aadfunc.md) | - | Workbooks |
| [`auditLogEvents`](../tables/auditlogevents.md) | - | Workbooks |
| [`domainLookback`](../tables/domainlookback.md) | - | Workbooks |
| [`managedservicesresources`](../tables/managedservicesresources.md) | - | Workbooks |
| [`recentActivity`](../tables/recentactivity.md) | - | Workbooks |
| [`signIns`](../tables/signins.md) | - | Workbooks |

### Internal Tables

The following **5 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | - | Hunting, Workbooks |
| [`IdentityInfo`](../tables/identityinfo.md) | - | Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft 365 Insider Risk Management](../connectors/officeirm.md) | Analytics, Hunting, Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Analytics, Workbooks |
| [`Watchlist`](../tables/watchlist.md) | - | Workbooks |

## Content Items

This solution includes **12 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Hunting Queries | 5 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Insider Risk_High User Security Alert Correlations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskHighUserAlertsCorrelation.yaml) | Medium | Execution | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Insider Risk_High User Security Incidents Correlation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskHighUserIncidentsCorrelation.yaml) | High | Execution | *Internal use:*<br>[`SecurityIncident`](../tables/securityincident.md) |
| [Insider Risk_Microsoft Purview Insider Risk Management Alert Observed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskM365IRMAlertObserved.yaml) | High | Execution | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Insider Risk_Risky User Access By Application](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskyAccessByApplication.yaml) | Medium | Execution | [`SigninLogs`](../tables/signinlogs.md) |
| [Insider Risk_Sensitive Data Access Outside Organizational Geo-location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Analytic%20Rules/InsiderRiskSensitiveDataAccessOutsideOrgGeo.yaml) | High | Exfiltration | [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Insider Risk_Entity Anomaly Followed by IRM Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderEntityAnomalyFollowedByIRMAlert.yaml) | PrivilegeEscalation | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Insider Risk_ISP Anomaly to Exfil](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderISPAnomalyCorrelatedToExfiltrationAlert.yaml) | Exfiltration | *Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Insider Risk_Multiple Entity-Based Anomalies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderMultipleEntityAnomalies.yaml) | PrivilegeEscalation | [`Uncommon`](../tables/uncommon.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md) |
| [Insider Risk_Possible Sabotage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderPossibleSabotage.yaml) | Impact | [`AzureActivity`](../tables/azureactivity.md) |
| [Insider Risk_Sign In Risk Followed By Sensitive Data Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Hunting%20Queries/InsiderSignInRiskFollowedBySensitiveDataAccessyaml.yaml) | Exfiltration | [`SigninLogs`](../tables/signinlogs.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [InsiderRiskManagement](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Workbooks/InsiderRiskManagement.json) | [`AADUserRiskEvents`](../tables/aaduserriskevents.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`AzureActivity`](../tables/azureactivity.md)<br>[`Correlate`](../tables/correlate.md)<br>[`InitialDataSet`](../tables/initialdataset.md)<br>[`LAQueryLogs`](../tables/laquerylogs.md)<br>[`LogOns`](../tables/logons.md)<br>[`MicrosoftPurviewInformationProtection`](../tables/microsoftpurviewinformationprotection.md)<br>[`NewUserAddsUser`](../tables/newuseraddsuser.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`PasswordResetMultiDataSource`](../tables/passwordresetmultidatasource.md)<br>[`RareAudits`](../tables/rareaudits.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`Uncommon`](../tables/uncommon.md)<br>[`UserAddWithResource`](../tables/useraddwithresource.md)<br>[`aadFunc`](../tables/aadfunc.md)<br>[`auditLogEvents`](../tables/auditlogevents.md)<br>[`domainLookback`](../tables/domainlookback.md)<br>[`managedservicesresources`](../tables/managedservicesresources.md)<br>[`recentActivity`](../tables/recentactivity.md)<br>[`signIns`](../tables/signins.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md)<br>[`Watchlist`](../tables/watchlist.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Notify-InsiderRiskTeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/Playbooks/Notify_InsiderRiskTeam/Notify_InsiderRiskTeam.json) | This playbook should be configured as an automation action with the Insider Risk Management Analytic... | - |

## Additional Documentation

> 📄 *Source: [MicrosoftPurviewInsiderRiskManagement/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftPurviewInsiderRiskManagement/README.md)*

## Overview
The Microsoft Sentinel: Insider Risk Management Solution demonstrates the “better together” story between Microsoft Purview Insider Risk Management and Microsoft Sentinel. The solution includes (1) Workbook, (5) Hunting Queries, (5) Analytics Rules, and (1) Playbook. Insider risk management helps minimize internal risks by enabling you to detect, investigate, and act on malicious and inadvertent activities in your organization. Insider risk policies allow you to define the types of risks to identify and detect in your organization, including acting on cases and act on cases including the ability to escalate cases to Microsoft Advanced eDiscovery. Risk analysts in your organization can quickly take appropriate actions to make sure users are compliant with your organization's compliance standards. Insider risks come in various forms including both witting (intentional) and unwitting (unintentional).This workbook provides an automated visualization of Insider risk behavior cross walked to Microsoft security offerings. This solution is enhanced when integrated with complimentary Microsoft Offerings such as💡 [Microsoft Purview Insider Risk Management](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management-solution-overview), 💡 [Communications Compliance](https://docs.microsoft.com/microsoft-365/compliance/communication-compliance-solution-overview), 💡 [Microsoft Information Protection](https://docs.microsoft.com/microsoft-365/compliance/information-protection), 💡 [Advanced eDiscovery](https://docs.microsoft.com/microsoft-365/compliance/ediscovery), and 💡 [Microsoft Sentinel Notebooks](https://docs.microsoft.com/azure/sentinel/notebooks). This workbook enables Insider Risk Teams, SecOps Analysts, and MSSPs to gain situational awareness for insider risk management, UEBA, device indicators, physical access, and HR signals. This workbook is designed to augment staffing through automation, artificial intelligence, machine learning, query/alerting generation, and visualizations. For more information, see 💡 [Microsoft Purview Insider Risk Management](https://docs.microsoft.com/microsoft-365/compliance/insider-risk-management-solution-overview).

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoftPurviewInsiderRiskManagement%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMicrosoftPurviewInsiderRiskManagement%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|
| 3.0.6       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |
| 3.0.5       | 10-04-2024                     | Updated Entity Mappings InsiderRiskyAccessByApplication.yaml             |
| 3.0.4       | 07-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID. |
| 3.0.3       | 10-10-2023                     | Updated **Workbook** template to replace the datatype InformationProtectionLogs_CL to MicrosoftPurviewInformationProtection                                                                                     |
| 3.0.2       | 04-10-2023                     | Updated **Workbook** template to fix Signinlogs datatype                 |
| 3.0.1       | 20-09-2023                     | Updated **Workbook** template to fix the invaild json issue              |
| 3.0.0       | 17-07-2023                     | Updating **Analytic Rules** with grouping configuration(Single Alert)    |
|             |                                |                                                                          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
