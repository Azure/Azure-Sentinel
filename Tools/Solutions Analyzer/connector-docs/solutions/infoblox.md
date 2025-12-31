# Infoblox

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Infoblox |
| **Support Tier** | Partner |
| **Support Link** | [https://support.infoblox.com/](https://support.infoblox.com/) |
| **Categories** | domains |
| **First Published** | 2024-07-15 |
| **Last Updated** | 2024-07-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox) |

## Data Connectors

This solution provides **5 data connector(s)**:

- [[Recommended] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md)
- [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md)
- [[Recommended] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md)
- [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md)
- [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md)

## Tables Reference

This solution uses **27 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md) | - | Workbooks |
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Infoblox SOC Insight Data Connector via Legacy Agent](../connectors/infobloxsocinsightsdataconnector-legacy.md), [[Recommended] Infoblox Cloud Data Connector via AMA](../connectors/infobloxclouddataconnectorama.md), [[Recommended] Infoblox SOC Insight Data Connector via AMA](../connectors/infobloxsocinsightsdataconnector-ama.md) | Analytics, Playbooks, Workbooks |
| [`Failed_Range_To_Ingest_CL`](../tables/failed-range-to-ingest-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | - |
| [`Host_Name_Info_CL`](../tables/host-name-info-cl.md) | - | Workbooks |
| [`IP_Space_Info_CL`](../tables/ip-space-info-cl.md) | - | Workbooks |
| [`Infoblox_Config_Insight_Details_CL`](../tables/infoblox-config-insight-details-cl.md) | - | Workbooks |
| [`Infoblox_Config_Insights_CL`](../tables/infoblox-config-insights-cl.md) | - | Workbooks |
| [`Infoblox_Failed_Indicators_CL`](../tables/infoblox-failed-indicators-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | - |
| [`Service_Name_Info_CL`](../tables/service-name-info-cl.md) | - | Workbooks |
| [`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md) | - | Workbooks |
| [`dossier_atp_CL`](../tables/dossier-atp-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_atp_threat_CL`](../tables/dossier-atp-threat-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_dns_CL`](../tables/dossier-dns-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_geo_CL`](../tables/dossier-geo-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_infoblox_web_cat_CL`](../tables/dossier-infoblox-web-cat-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_inforank_CL`](../tables/dossier-inforank-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_malware_analysis_v3_CL`](../tables/dossier-malware-analysis-v3-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_nameserver_CL`](../tables/dossier-nameserver-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_nameserver_matches_CL`](../tables/dossier-nameserver-matches-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_ptr_CL`](../tables/dossier-ptr-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_rpz_feeds_CL`](../tables/dossier-rpz-feeds-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_rpz_feeds_records_CL`](../tables/dossier-rpz-feeds-records-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_threat_actor_CL`](../tables/dossier-threat-actor-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_tld_risk_CL`](../tables/dossier-tld-risk-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_whitelist_CL`](../tables/dossier-whitelist-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`dossier_whois_CL`](../tables/dossier-whois-cl.md) | [Infoblox Data Connector via REST API](../connectors/infobloxdataconnector.md) | Workbooks |
| [`incidents`](../tables/incidents.md) | - | Workbooks |

### Internal Tables

The following **8 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`InfobloxInsightAssets_CL`](../tables/infobloxinsightassets-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsightComments_CL`](../tables/infobloxinsightcomments-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsightEvents_CL`](../tables/infobloxinsightevents-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsightIndicators_CL`](../tables/infobloxinsightindicators-cl.md) | - | Playbooks (writes), Workbooks |
| [`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) | [Infoblox SOC Insight Data Connector via REST API](../connectors/infobloxsocinsightsdataconnector-api.md) | Analytics, Playbooks (writes), Workbooks |
| [`SecurityAlert`](../tables/securityalert.md) | - | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |
| [`tide_lookup_data_CL`](../tables/tide-lookup-data-cl.md) | - | Playbooks (writes), Workbooks |

## Content Items

This solution includes **27 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 17 |
| Parsers | 6 |
| Analytic Rules | 2 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Infoblox - SOC Insight Detected - API Source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Analytic%20Rules/Infoblox-SOCInsight-Detected-APISource.yaml) | Medium | Impact | *Internal use:*<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) |
| [Infoblox - SOC Insight Detected - CDC Source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Analytic%20Rules/Infoblox-SOCInsight-Detected-CDCSource.yaml) | Medium | Impact | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Infoblox_Lookup_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Workbooks/Infoblox_Lookup_Workbook.json) | [`dossier_atp_CL`](../tables/dossier-atp-cl.md)<br>[`dossier_atp_threat_CL`](../tables/dossier-atp-threat-cl.md)<br>[`dossier_dns_CL`](../tables/dossier-dns-cl.md)<br>[`dossier_geo_CL`](../tables/dossier-geo-cl.md)<br>[`dossier_infoblox_web_cat_CL`](../tables/dossier-infoblox-web-cat-cl.md)<br>[`dossier_inforank_CL`](../tables/dossier-inforank-cl.md)<br>[`dossier_malware_analysis_v3_CL`](../tables/dossier-malware-analysis-v3-cl.md)<br>[`dossier_nameserver_CL`](../tables/dossier-nameserver-cl.md)<br>[`dossier_nameserver_matches_CL`](../tables/dossier-nameserver-matches-cl.md)<br>[`dossier_ptr_CL`](../tables/dossier-ptr-cl.md)<br>[`dossier_rpz_feeds_CL`](../tables/dossier-rpz-feeds-cl.md)<br>[`dossier_rpz_feeds_records_CL`](../tables/dossier-rpz-feeds-records-cl.md)<br>[`dossier_threat_actor_CL`](../tables/dossier-threat-actor-cl.md)<br>[`dossier_tld_risk_CL`](../tables/dossier-tld-risk-cl.md)<br>[`dossier_whitelist_CL`](../tables/dossier-whitelist-cl.md)<br>[`dossier_whois_CL`](../tables/dossier-whois-cl.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md)<br>[`tide_lookup_data_CL`](../tables/tide-lookup-data-cl.md) |
| [Infoblox_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Workbooks/Infoblox_Workbook.json) | [`AlertsWithTiObservables`](../tables/alertswithtiobservables.md)<br>[`CommonSecurityLog`](../tables/commonsecuritylog.md)<br>[`Host_Name_Info_CL`](../tables/host-name-info-cl.md)<br>[`IP_Space_Info_CL`](../tables/ip-space-info-cl.md)<br>[`Infoblox_Config_Insight_Details_CL`](../tables/infoblox-config-insight-details-cl.md)<br>[`Infoblox_Config_Insights_CL`](../tables/infoblox-config-insights-cl.md)<br>[`Service_Name_Info_CL`](../tables/service-name-info-cl.md)<br>[`ThreatIntelligenceIndicator`](../tables/threatintelligenceindicator.md)<br>[`incidents`](../tables/incidents.md)<br>*Internal use:*<br>[`InfobloxInsightAssets_CL`](../tables/infobloxinsightassets-cl.md)<br>[`InfobloxInsightComments_CL`](../tables/infobloxinsightcomments-cl.md)<br>[`InfobloxInsightEvents_CL`](../tables/infobloxinsightevents-cl.md)<br>[`InfobloxInsightIndicators_CL`](../tables/infobloxinsightindicators-cl.md)<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md)<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Infoblox-Block-Allow-IP-Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Block%20Allow%20IP%20Domain/azuredeploy.json) | The playbook will add/remove IP or Domain value in Named List of Infoblox. | - |
| [Infoblox-Block-Allow-IP-Domain-Incident-Based](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Block%20Allow%20IP%20Domain%20Incident%20Based/azuredeploy.json) | The playbook will add / remove IP or Domain values in Named List that available in incidents of Info... | - |
| [Infoblox-Config-Insight-Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/InfoBlox%20Config%20Insight%20Details/azuredeploy.json) | The playbook retrieves Config Insight Details Data and ingests it into a custom table within the Log... | - |
| [Infoblox-Config-Insights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Config%20Insights/azuredeploy.json) | The playbook retrieves Config Insight Data and ingests it into a custom table within the Log Analyti... | - |
| [Infoblox-DHCP-Lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20DHCP%20Lookup/azuredeploy.json) | The playbook will retrieve IP entities from an incident, search for related DHCP data in a table, an... | [`CommonSecurityLog`](../tables/commonsecuritylog.md) *(read)* |
| [Infoblox-Data-Connector-Trigger-Sync](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Data%20Connector%20Trigger%20Sync/azuredeploy.json) | Playbook to sync timer trigger of all Infoblox data connectors. | - |
| [Infoblox-Get-Host-Name](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Get%20Host%20Name/azuredeploy.json) | The playbook will fetch the data from 'Hosts' API and ingest it into custom table | - |
| [Infoblox-Get-IP-Space-Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Get%20IP%20Space%20Data/azuredeploy.json) | The playbook will fetch the data from 'IP Space' API and ingest it into custom table | - |
| [Infoblox-Get-Service-Name](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20Get%20Service%20Name/azuredeploy.json) | This playbook will fetch the data from 'Services' API and ingest it into custom table | - |
| [Infoblox-IPAM-Lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20IPAM%20Lookup/azuredeploy.json) | The playbook will retrieve IP entities from an incident, call an API to obtain IPAM lookup data, and... | - |
| [Infoblox-SOC-Get-Insight-Details](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20SOC%20Get%20Insight%20Details/azuredeploy.json) | Leverages the Infoblox SOC Insights API to enrich a Microsoft Sentinel Incident triggered by an Info... | *Internal use:*<br>[`InfobloxInsightAssets_CL`](../tables/infobloxinsightassets-cl.md) *(write)*<br>[`InfobloxInsightComments_CL`](../tables/infobloxinsightcomments-cl.md) *(write)*<br>[`InfobloxInsightEvents_CL`](../tables/infobloxinsightevents-cl.md) *(write)*<br>[`InfobloxInsightIndicators_CL`](../tables/infobloxinsightindicators-cl.md) *(write)*<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) *(write)* |
| [Infoblox-SOC-Get-Open-Insights-API](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20SOC%20Get%20Open%20Insights%20API/azuredeploy.json) | Leverages the Infoblox SOC Insights API to ingest all Open/Active SOC Insights at time of run into t... | *Internal use:*<br>[`InfobloxInsight_CL`](../tables/infobloxinsight-cl.md) *(write)* |
| [Infoblox-SOC-Import-Indicators-TI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20SOC%20Import%20Indicators%20TI/azuredeploy.json) | Imports each Indicator of a Microsoft Sentinel Incident triggered by an Infoblox SOC Insight into th... | - |
| [Infoblox-TIDE-Lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20TIDE%20Lookup/azuredeploy.json) | The playbook fetches TIDE lookup data for the provided entity type and value. | *Internal use:*<br>[`tide_lookup_data_CL`](../tables/tide-lookup-data-cl.md) *(read/write)* |
| [Infoblox-TIDE-Lookup-Comment-Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20TIDE%20Lookup%20Incident%20Comment%20Based/azuredeploy.json) | The playbook enrich an incident by adding TIDE Lookup information as comment on an incident. | - |
| [Infoblox-TIDE-Lookup-Via-Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20TIDE%20Lookup%20Incident%20Based/azuredeploy.json) | The playbook takes entity type and value from incident available in Workbook and ingests TIDE Lookup... | - |
| [Infoblox-TimeRangeBased-DHCP-Lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Playbooks/Infoblox%20TimeRangeBased%20DHCP%20Lookup/azuredeploy.json) | The playbook will retrieve IP entities from an incident, search for related DHCP data in a table for... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [InfobloxCDC_SOCInsights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Parsers/InfobloxCDC_SOCInsights.yaml) | - | - |
| [InfobloxInsight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Parsers/InfobloxInsight.yaml) | - | - |
| [InfobloxInsightAssets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Parsers/InfobloxInsightAssets.yaml) | - | - |
| [InfobloxInsightComments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Parsers/InfobloxInsightComments.yaml) | - | - |
| [InfobloxInsightEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Parsers/InfobloxInsightEvents.yaml) | - | - |
| [InfobloxInsightIndicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Infoblox/Parsers/InfobloxInsightIndicators.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       |   19-06-2025                   | Added flags for Asset, Indicator, Event and Comment in InfobloxSOCGetInsightDetails playbook. Updated Workbook, Parser and Analytic rule.           |
| 3.0.1       |   07-11-2024                   | Bug fix in Infoblox_Workbook **Workbook**   |
| 3.0.0       |   15-07-2024                   | Initial Solution Release                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
