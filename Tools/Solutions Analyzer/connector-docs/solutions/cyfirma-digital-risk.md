# Cyfirma Digital Risk

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-03-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md)

## Tables Reference

This solution uses **7 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyfirmaDBWMDarkWebAlerts_CL`](../tables/cyfirmadbwmdarkwebalerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |
| [`CyfirmaDBWMPhishingAlerts_CL`](../tables/cyfirmadbwmphishingalerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |
| [`CyfirmaDBWMRansomwareAlerts_CL`](../tables/cyfirmadbwmransomwarealerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |
| [`CyfirmaSPEConfidentialFilesAlerts_CL`](../tables/cyfirmaspeconfidentialfilesalerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |
| [`CyfirmaSPEPIIAndCIIAlerts_CL`](../tables/cyfirmaspepiiandciialerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |
| [`CyfirmaSPESocialThreatAlerts_CL`](../tables/cyfirmaspesocialthreatalerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |
| [`CyfirmaSPESourceCodeAlerts_CL`](../tables/cyfirmaspesourcecodealerts-cl.md) | [CYFIRMA Digital Risk](../connectors/cyfirmadigitalriskalertsconnector.md) | Analytics |

## Content Items

This solution includes **14 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 14 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CYFIRMA - Data Breach and Web Monitoring - Dark Web High Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/DBWMDarkWebHighRule.yaml) | High | CredentialAccess, Collection, Exfiltration, Impact | [`CyfirmaDBWMDarkWebAlerts_CL`](../tables/cyfirmadbwmdarkwebalerts-cl.md) |
| [CYFIRMA - Data Breach and Web Monitoring - Dark Web Medium Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/DBWMDarkWebMediumRule.yaml) | Medium | CredentialAccess, Collection, Exfiltration, Impact | [`CyfirmaDBWMDarkWebAlerts_CL`](../tables/cyfirmadbwmdarkwebalerts-cl.md) |
| [CYFIRMA - Data Breach and Web Monitoring - Phishing Campaign Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/DBWMPhishingCampaignDetectionHighRule.yaml) | High | InitialAccess, Exfiltration | [`CyfirmaDBWMPhishingAlerts_CL`](../tables/cyfirmadbwmphishingalerts-cl.md) |
| [CYFIRMA - Data Breach and Web Monitoring - Phishing Campaign Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/DBWMPhishingCampaignDetectionMediumRule.yaml) | Medium | InitialAccess, Exfiltration | [`CyfirmaDBWMPhishingAlerts_CL`](../tables/cyfirmadbwmphishingalerts-cl.md) |
| [CYFIRMA - Data Breach and Web Monitoring - Ransomware Exposure Detected Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/DBWMRansomwareExposureDetectedHighRule.yaml) | High | InitialAccess, Exfiltration | [`CyfirmaDBWMRansomwareAlerts_CL`](../tables/cyfirmadbwmransomwarealerts-cl.md) |
| [CYFIRMA - Data Breach and Web Monitoring - Ransomware Exposure Detected Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/DBWMRansomwareExposureDetectedMediumRule.yaml) | Medium | InitialAccess, Exfiltration | [`CyfirmaDBWMRansomwareAlerts_CL`](../tables/cyfirmadbwmransomwarealerts-cl.md) |
| [CYFIRMA - Social and Public Exposure -  Social Media Threats  Activity Detected Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPESocialMediaThreatsHighRule.yaml) | High | ResourceDevelopment, Reconnaissance, InitialAccess, Impact | [`CyfirmaSPESocialThreatAlerts_CL`](../tables/cyfirmaspesocialthreatalerts-cl.md) |
| [CYFIRMA - Social and Public Exposure -  Social Media Threats  Activity Detected Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPESocialMediaThreatsMediumRule.yaml) | Medium | ResourceDevelopment, Reconnaissance, InitialAccess, Impact | [`CyfirmaSPESocialThreatAlerts_CL`](../tables/cyfirmaspesocialthreatalerts-cl.md) |
| [CYFIRMA - Social and Public Exposure - Confidential Files Information Exposure Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPEConfidentialFilesHighRule.yaml) | High | InitialAccess, Exfiltration, Collection, Reconnaissance | [`CyfirmaSPEConfidentialFilesAlerts_CL`](../tables/cyfirmaspeconfidentialfilesalerts-cl.md) |
| [CYFIRMA - Social and Public Exposure - Confidential Files Information Exposure Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPEConfidentialFilesMediumRule.yaml) | Medium | InitialAccess, Exfiltration, Collection, Reconnaissance | [`CyfirmaSPEConfidentialFilesAlerts_CL`](../tables/cyfirmaspeconfidentialfilesalerts-cl.md) |
| [CYFIRMA - Social and Public Exposure - Exposure of PII/CII in Public Domain Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPEExposureOfPIICIIHighRule.yaml) | High | InitialAccess, Exfiltration, Collection, CredentialAccess | [`CyfirmaSPEPIIAndCIIAlerts_CL`](../tables/cyfirmaspepiiandciialerts-cl.md) |
| [CYFIRMA - Social and Public Exposure - Exposure of PII/CII in Public Domain Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPEExposureOfPIICIIMediumRule.yaml) | Medium | InitialAccess, Exfiltration, Collection, CredentialAccess | [`CyfirmaSPEPIIAndCIIAlerts_CL`](../tables/cyfirmaspepiiandciialerts-cl.md) |
| [CYFIRMA - Social and Public Exposure - Source Code Exposure on Public Repositories Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPESourceCodeExposureHighRule.yaml) | High | ResourceDevelopment, CredentialAccess, Discovery | [`CyfirmaSPESourceCodeAlerts_CL`](../tables/cyfirmaspesourcecodealerts-cl.md) |
| [CYFIRMA - Social and Public Exposure - Source Code Exposure on Public Repositories Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Digital%20Risk/Analytic%20Rules/SPESourceCodeExposureMediumRule.yaml) | Medium | ResourceDevelopment, CredentialAccess, Discovery | [`CyfirmaSPESourceCodeAlerts_CL`](../tables/cyfirmaspesourcecodealerts-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.3       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.2       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.1       | 17-06-2025                     | Minor changes to **CCF Data Connector**.                               |
| 3.0.0       | 14-04-2025                     | Initial Solution Release.                                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
