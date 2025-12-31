# MaturityModelForEventLogManagementM2131

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-12-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **69 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`AADManagedIdentitySignInLogs`](../tables/aadmanagedidentitysigninlogs.md) | Workbooks |
| [`AADServicePrincipalSignInLogs`](../tables/aadserviceprincipalsigninlogs.md) | Workbooks |
| [`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md) | Workbooks |
| [`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md) | Workbooks |
| [`AWSCloudTrail`](../tables/awscloudtrail.md) | Workbooks |
| [`AWSGuardDuty`](../tables/awsguardduty.md) | Workbooks |
| [`AWSVPCFlow`](../tables/awsvpcflow.md) | Workbooks |
| [`AZFWDnsQuery`](../tables/azfwdnsquery.md) | Workbooks |
| [`AuditLogs`](../tables/auditlogs.md) | Workbooks |
| [`AzureActivity`](../tables/azureactivity.md) | Analytics, Workbooks |
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | Workbooks |
| [`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md) | Workbooks |
| [`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md) | Workbooks |
| [`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md) | Workbooks |
| [`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md) | Workbooks |
| [`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md) | Workbooks |
| [`CloudAppEvents`](../tables/cloudappevents.md) | Workbooks |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | Workbooks |
| [`ConfigurationChange`](../tables/configurationchange.md) | Workbooks |
| [`ConfigurationData`](../tables/configurationdata.md) | Workbooks |
| [`Corelight_CL`](../tables/corelight-cl.md) | Workbooks |
| [`Crosswalk`](../tables/crosswalk.md) | Workbooks |
| [`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md) | Workbooks |
| [`DeviceNetworkEvents`](../tables/devicenetworkevents.md) | Workbooks |
| [`DeviceNetworkInfo`](../tables/devicenetworkinfo.md) | Workbooks |
| [`DeviceProcessEvents`](../tables/deviceprocessevents.md) | Workbooks |
| [`DnsEvents`](../tables/dnsevents.md) | Workbooks |
| [`EmailEvents`](../tables/emailevents.md) | Workbooks |
| [`Event`](../tables/event.md) | Workbooks |
| [`EventsData`](../tables/eventsdata.md) | Workbooks |
| [`FakeData`](../tables/fakedata.md) | Workbooks |
| [`GCP_DNS_CL`](../tables/gcp-dns-cl.md) | Workbooks |
| [`GCP_IAM_CL`](../tables/gcp-iam-cl.md) | Workbooks |
| [`Heartbeat`](../tables/heartbeat.md) | Analytics |
| [`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md) | Workbooks |
| [`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md) | Workbooks |
| [`IntuneAuditLogs`](../tables/intuneauditlogs.md) | Workbooks |
| [`IntuneOperationalLogs`](../tables/intuneoperationallogs.md) | Workbooks |
| [`KubeEvents_CL`](../tables/kubeevents-cl.md) | Workbooks |
| [`LogOns`](../tables/logons.md) | Workbooks |
| [`NTANetAnalytics`](../tables/ntanetanalytics.md) | Workbooks |
| [`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md) | Workbooks |
| [`OfficeActivity`](../tables/officeactivity.md) | Workbooks |
| [`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md) | Workbooks |
| [`RawNetworkEvents`](../tables/rawnetworkevents.md) | Workbooks |
| [`SecurityEvent`](../tables/securityevent.md) | Workbooks |
| [`SecurityIoTRawEvent`](../tables/securityiotrawevent.md) | Workbooks |
| [`SecurityRecommendation`](../tables/securityrecommendation.md) | Analytics, Workbooks |
| [`SentinelOne_CL`](../tables/sentinelone-cl.md) | Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | Workbooks |
| [`StorageBlobLogs`](../tables/storagebloblogs.md) | Workbooks |
| [`StorageFileLogs`](../tables/storagefilelogs.md) | Workbooks |
| [`Syslog`](../tables/syslog.md) | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | Workbooks |
| [`Uncommon`](../tables/uncommon.md) | Workbooks |
| [`Update`](../tables/update.md) | Workbooks |
| [`Usage`](../tables/usage.md) | Analytics, Hunting |
| [`VMConnection`](../tables/vmconnection.md) | Workbooks |
| [`VMProcess`](../tables/vmprocess.md) | Workbooks |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | Workbooks |
| [`WindowsEvent`](../tables/windowsevent.md) | Workbooks |
| [`barracuda_CL`](../tables/barracuda-cl.md) | Workbooks |
| [`managedservicesresources`](../tables/managedservicesresources.md) | Workbooks |
| [`meraki_CL`](../tables/meraki-cl.md) | Workbooks |
| [`parsedData`](../tables/parseddata.md) | Workbooks |
| [`requests`](../tables/requests.md) | Workbooks |
| [`securityresources`](../tables/securityresources.md) | Workbooks |
| [`topItems`](../tables/topitems.md) | Workbooks |
| [`totable`](../tables/totable.md) | Workbooks |

### Internal Tables

The following **4 table(s)** are used internally by this solution's playbooks:

| Table | Used By Content |
|-------|----------------|
| [`BehaviorAnalytics`](../tables/behavioranalytics.md) | Workbooks |
| [`IdentityInfo`](../tables/identityinfo.md) | Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | Workbooks |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 8 |
| Hunting Queries | 4 |
| Playbooks | 3 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [M2131_AssetStoppedLogging](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131AssetStoppedLogging.yaml) | Medium | Discovery | [`Heartbeat`](../tables/heartbeat.md) |
| [M2131_DataConnectorAddedChangedRemoved](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131DataConnectorAddedChangedRemoved.yaml) | Medium | Discovery | [`AzureActivity`](../tables/azureactivity.md) |
| [M2131_EventLogManagementPostureChanged_EL0](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131EventLogManagementPostureChangedEL0.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |
| [M2131_EventLogManagementPostureChanged_EL1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131EventLogManagementPostureChangedEL1.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |
| [M2131_EventLogManagementPostureChanged_EL2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131EventLogManagementPostureChangedEL2.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |
| [M2131_EventLogManagementPostureChanged_EL3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131EventLogManagementPostureChangedEL3.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |
| [M2131_LogRetentionLessThan1Year](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131LogRetentionLessThan1Year.yaml) | Medium | Discovery | [`SecurityRecommendation`](../tables/securityrecommendation.md) |
| [M2131_RecommendedDatatableUnhealthy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Analytic%20Rules/M2131RecommendedDatatableUnhealthy.yaml) | Medium | Discovery | [`Usage`](../tables/usage.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [M2131_RecommendedDatatableNotLogged_EL0](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Hunting%20Queries/M2131RecommendedDatatableNotLoggedEL0.yaml) | Discovery | [`Usage`](../tables/usage.md) |
| [M2131_RecommendedDatatableNotLogged_EL1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Hunting%20Queries/M2131RecommendedDatatableNotLoggedEL1.yaml) | Discovery | [`Usage`](../tables/usage.md) |
| [M2131_RecommendedDatatableNotLogged_EL2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Hunting%20Queries/M2131RecommendedDatatableNotLoggedEL2.yaml) | Discovery | [`Usage`](../tables/usage.md) |
| [M2131_RecommendedDatatableNotLogged_EL3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Hunting%20Queries/M2131RecommendedDatatableNotLoggedEL3.yaml) | Discovery | [`Usage`](../tables/usage.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [MaturityModelForEventLogManagement_M2131](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/MaturityModelForEventLogManagement_M2131.json) | [`AADManagedIdentitySignInLogs`](../tables/aadmanagedidentitysigninlogs.md)<br>[`AADServicePrincipalSignInLogs`](../tables/aadserviceprincipalsigninlogs.md)<br>[`ASimDnsActivityLogs`](../tables/asimdnsactivitylogs.md)<br>[`ASimNetworkSessionLogs`](../tables/asimnetworksessionlogs.md)<br>[`AWSCloudTrail`](../tables/awscloudtrail.md)<br>[`AWSGuardDuty`](../tables/awsguardduty.md)<br>[`AWSVPCFlow`](../tables/awsvpcflow.md)<br>[`AZFWDnsQuery`](../tables/azfwdnsquery.md)<br>[`AuditLogs`](../tables/auditlogs.md)<br>[`AzureActivity`](../tables/azureactivity.md)<br>[`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`AzureNetworkAnalytics_CL`](../tables/azurenetworkanalytics-cl.md)<br>[`CarbonBlackEvents_CL`](../tables/carbonblackevents-cl.md)<br>[`CarbonBlackNotifications_CL`](../tables/carbonblacknotifications-cl.md)<br>[`CarbonBlack_Alerts_CL`](../tables/carbonblack-alerts-cl.md)<br>[`Cisco_Umbrella_dns_CL`](../tables/cisco-umbrella-dns-cl.md)<br>[`CloudAppEvents`](../tables/cloudappevents.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`ConfigurationChange`](../tables/configurationchange.md)<br>[`ConfigurationData`](../tables/configurationdata.md)<br>[`Corelight_CL`](../tables/corelight-cl.md)<br>[`Crosswalk`](../tables/crosswalk.md)<br>[`DefenderIoTRawEvent`](../tables/defenderiotrawevent.md)<br>[`DeviceNetworkEvents`](../tables/devicenetworkevents.md)<br>[`DeviceNetworkInfo`](../tables/devicenetworkinfo.md)<br>[`DeviceProcessEvents`](../tables/deviceprocessevents.md)<br>[`DnsEvents`](../tables/dnsevents.md)<br>[`EmailEvents`](../tables/emailevents.md)<br>[`Event`](../tables/event.md)<br>[`EventsData`](../tables/eventsdata.md)<br>[`FakeData`](../tables/fakedata.md)<br>[`GCP_DNS_CL`](../tables/gcp-dns-cl.md)<br>[`GCP_IAM_CL`](../tables/gcp-iam-cl.md)<br>[`Illumio_Flow_Events_CL`](../tables/illumio-flow-events-cl.md)<br>[`InformationProtectionLogs_CL`](../tables/informationprotectionlogs-cl.md)<br>[`IntuneAuditLogs`](../tables/intuneauditlogs.md)<br>[`IntuneOperationalLogs`](../tables/intuneoperationallogs.md)<br>[`KubeEvents_CL`](../tables/kubeevents-cl.md)<br>[`LogOns`](../tables/logons.md)<br>[`NTANetAnalytics`](../tables/ntanetanalytics.md)<br>[`NXLog_DNS_Server_CL`](../tables/nxlog-dns-server-cl.md)<br>[`OfficeActivity`](../tables/officeactivity.md)<br>[`QualysHostDetectionV3_CL`](../tables/qualyshostdetectionv3-cl.md)<br>[`RawNetworkEvents`](../tables/rawnetworkevents.md)<br>[`SecurityEvent`](../tables/securityevent.md)<br>[`SecurityIoTRawEvent`](../tables/securityiotrawevent.md)<br>[`SecurityRecommendation`](../tables/securityrecommendation.md)<br>[`SentinelOne_CL`](../tables/sentinelone-cl.md)<br>[`SigninLogs`](../tables/signinlogs.md)<br>[`StorageBlobLogs`](../tables/storagebloblogs.md)<br>[`StorageFileLogs`](../tables/storagefilelogs.md)<br>[`Syslog`](../tables/syslog.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`Uncommon`](../tables/uncommon.md)<br>[`Update`](../tables/update.md)<br>[`VMConnection`](../tables/vmconnection.md)<br>[`VMProcess`](../tables/vmprocess.md)<br>[`VectraStream_CL`](../tables/vectrastream-cl.md)<br>[`WindowsEvent`](../tables/windowsevent.md)<br>[`barracuda_CL`](../tables/barracuda-cl.md)<br>[`managedservicesresources`](../tables/managedservicesresources.md)<br>[`meraki_CL`](../tables/meraki-cl.md)<br>[`parsedData`](../tables/parseddata.md)<br>[`requests`](../tables/requests.md)<br>[`securityresources`](../tables/securityresources.md)<br>[`topItems`](../tables/topitems.md)<br>[`totable`](../tables/totable.md)<br>*Internal use:*<br>[`BehaviorAnalytics`](../tables/behavioranalytics.md)<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Jira Issue](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Playbooks/Open_JIRATicketRecommendation-M2131/Open_JIRATicketRecommendation-M2131.json) | This playbook will open a Jira Issue when a new incident is opened in Microsoft Sentinel. | - |
| [Create-AzureDevOpsTask](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Playbooks/Open_DevOpsTaskRecommendation-M2131/Open_DevOpsTaskRecommendation-M2131.json) | This playbook will create the Azure DevOps task filled with the Microsoft Sentinel incident details. | - |
| [Notify-LogManagementTeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Playbooks/Notify_LogManagementTeam-MaturityModel/Notify_LogManagementTeam.json) | This Security Orchestration, Automation, & Response (SOAR) capability is designed for configuration ... | - |

## Additional Documentation

> 📄 *Source: [MaturityModelForEventLogManagementM2131/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/README.md)*

# Overview
---
## Microsoft Sentinel: Maturity Model for Event Log Management (M-21-31) Solution
This solution is designed to enable Cloud Architects, Security Engineers, and Governance Risk Compliance Professionals to increase visibility before, during, and after a cybersecurity incident. The solution includes (1) workbook, (4) hunting queries, (8) analytics rules, and (3) playbooks providing a comprehensive approach to design, build, monitoring, and response in logging architectures. Information from logs on information systems1 (for both on-premises systems and connections hosted by third parties, such as cloud services providers (CSPs) is invaluable in the detection, investigation, and remediation of cyber threats. "Executive Order 14028, Improving the Nation's Cybersecurity, directs decisive action to improve the Federal Government’s investigative and remediation capabilities. This memorandum was developed in accordance with and addresses the requirements in section 8 of the Executive Order for logging, log retention, and log management, with a focus on ensuring centralized access and visibility for the highest-level enterprise security operations center (SOC) of each agency. In addition, this memorandum establishes requirements for agencies3 to increase the sharing of such information, as needed and appropriate, to accelerate incident response efforts and to enable more effective defense of Federal information and executive branch departments and agencies." For more information, see 💡[Improving the Federal Government’s Investigative and Remediation Capabilities Related to Cybersecurity Incidents (M-21-31)](https://www.whitehouse.gov/wp-content/uploads/2021/08/M-21-31-Improving-the-Federal-Governments-Investigative-and-Remediation-Capabilities-Related-to-Cybersecurity-Incidents.pdf).

## Try on Portal
You can deploy the solution by clicking on the buttons below:

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMaturityModelForEventLogManagementM2131%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMaturityModelForEventLogManagementM2131%2FPackage%2FmainTemplate.json" target="_blank"><img src="https://aka.ms/deploytoazuregovbutton"/></a>

![Workbook Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MaturityModelForEventLogManagementM2131/Workbooks/Images/MaturityModelForEventLogManagement_M2131Black.png?raw=true)

## Getting Started

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**    |
|-------------|--------------------------------|-----------------------|
| 3.0.3       | 26-09-2025                     | Updated the broken metrics in the workbook                      |
| 3.0.2       | 31-01-2024                     | Updated the solution to fix Analytic Rules deployment issue     |
| 3.0.1       | 09-11-2023                     | Changes for rebranding from Azure Active Directory Identity Protection to Microsoft Entra ID Protection    |
| 3.0.0       | 20-07-2023                     | Updated **Workbook** template to remove unused variables.      |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
