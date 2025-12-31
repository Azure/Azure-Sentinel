# Team Cymru Scout

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Team Cymru |
| **Support Tier** | Partner |
| **Support Link** | [http://team-cymru.com](http://team-cymru.com) |
| **Categories** | domains |
| **First Published** | 2024-07-16 |
| **Last Updated** | 2025-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md)

## Tables Reference

This solution uses **23 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Cymru_Scout_Account_Usage_Data_CL`](../tables/cymru-scout-account-usage-data-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | Workbooks |
| [`Cymru_Scout_Domain_Data_CL`](../tables/cymru-scout-domain-data-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | Workbooks |
| [`Cymru_Scout_IP_Data_Communications_CL`](../tables/cymru-scout-ip-data-communications-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Details_CL`](../tables/cymru-scout-ip-data-details-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Fingerprints_CL`](../tables/cymru-scout-ip-data-fingerprints-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Foundation_CL`](../tables/cymru-scout-ip-data-foundation-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_OpenPorts_CL`](../tables/cymru-scout-ip-data-openports-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_PDNS_CL`](../tables/cymru-scout-ip-data-pdns-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Summary_Certs_CL`](../tables/cymru-scout-ip-data-summary-certs-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Summary_Details_CL`](../tables/cymru-scout-ip-data-summary-details-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Summary_Fingerprints_CL`](../tables/cymru-scout-ip-data-summary-fingerprints-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Summary_OpenPorts_CL`](../tables/cymru-scout-ip-data-summary-openports-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_Summary_PDNS_CL`](../tables/cymru-scout-ip-data-summary-pdns-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Cymru_Scout_IP_Data_x509_CL`](../tables/cymru-scout-ip-data-x509-cl.md) | [Team Cymru Scout Data Connector](../connectors/teamcymruscout.md) | - |
| [`Domain_Data_CL`](../tables/domain-data-cl.md) | - | Workbooks |
| [`InsightsMessageTable`](../tables/insightsmessagetable.md) | - | Workbooks |
| [`Open_Ports_Data_CL`](../tables/open-ports-data-cl.md) | - | Workbooks |
| [`Proto_By_IP_Data_CL`](../tables/proto-by-ip-data-cl.md) | - | Workbooks |
| [`Summary_Details_CL`](../tables/summary-details-cl.md) | - | Workbooks |
| [`Summary_Details_Top_Certs_Data_CL`](../tables/summary-details-top-certs-data-cl.md) | - | Workbooks |
| [`insights_table_name`](../tables/insights-table-name.md) | - | Playbooks |
| [`ip_indicators_table_name`](../tables/ip-indicators-table-name.md) | - | Playbooks |
| [`pdns_table_name`](../tables/pdns-table-name.md) | - | Playbooks |

## Content Items

This solution includes **28 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 22 |
| Playbooks | 3 |
| Watchlists | 2 |
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [TeamCymruScout](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Workbooks/TeamCymruScout.json) | [`Cymru_Scout_Account_Usage_Data_CL`](../tables/cymru-scout-account-usage-data-cl.md)<br>[`Cymru_Scout_Domain_Data_CL`](../tables/cymru-scout-domain-data-cl.md)<br>[`Domain_Data_CL`](../tables/domain-data-cl.md)<br>[`InsightsMessageTable`](../tables/insightsmessagetable.md)<br>[`Open_Ports_Data_CL`](../tables/open-ports-data-cl.md)<br>[`Proto_By_IP_Data_CL`](../tables/proto-by-ip-data-cl.md)<br>[`Summary_Details_CL`](../tables/summary-details-cl.md)<br>[`Summary_Details_Top_Certs_Data_CL`](../tables/summary-details-top-certs-data-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Team Cymru Scout Create Incident And Notify](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Playbooks/TeamCymruScoutCreateIncidentAndNotify/azuredeploy.json) | This playbook will create an incident for suspicious or malicious ip and notify to pre-defined or us... | [`insights_table_name`](../tables/insights-table-name.md) *(read)* |
| [Team Cymru Scout Enrich Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Playbooks/TeamCymruScoutEnrichIncident/azuredeploy.json) | This playbook will fetch and ingest IP or Domain Indicator data based on Entity mapped in Microsoft ... | [`pdns_table_name`](../tables/pdns-table-name.md) *(read)* |
| [Team Cymru Scout Live Investigation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Playbooks/TeamCymruScoutLiveInvestigation/azuredeploy.json) | This playbook will fetch and ingest IP or Domain Indicator data based on input parameters given in t... | [`ip_indicators_table_name`](../tables/ip-indicators-table-name.md) *(read)* |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CymruScoutAccountUsage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutAccountUsage.yaml) | - | - |
| [CymruScoutCommunicationsData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutCommunicationsData.yaml) | - | - |
| [CymruScoutCorrelate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutCorrelate.yaml) | - | - |
| [CymruScoutDomain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutDomain.yaml) | - | - |
| [CymruScoutDomainData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutDomainData.yaml) | - | - |
| [CymruScoutFingerprintsData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutFingerprintsData.yaml) | - | - |
| [CymruScoutIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutIP.yaml) | - | - |
| [CymruScoutIdentity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutIdentity.yaml) | - | - |
| [CymruScoutOpenPortsData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutOpenPortsData.yaml) | - | - |
| [CymruScoutPdnsData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutPdnsData.yaml) | - | - |
| [CymruScoutProtoByIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutProtoByIP.yaml) | - | - |
| [CymruScoutSummary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutSummary.yaml) | - | - |
| [CymruScoutSummaryTopCerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutSummaryTopCerts.yaml) | - | - |
| [CymruScoutSummaryTopFingerprints](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutSummaryTopFingerprints.yaml) | - | - |
| [CymruScoutSummaryTopOpenPorts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutSummaryTopOpenPorts.yaml) | - | - |
| [CymruScoutSummaryTopPdns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutSummaryTopPdns.yaml) | - | - |
| [CymruScoutTopAsnsByIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutTopAsnsByIP.yaml) | - | - |
| [CymruScoutTopCountryCodesByIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutTopCountryCodesByIP.yaml) | - | - |
| [CymruScoutTopServicesByIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutTopServicesByIP.yaml) | - | - |
| [CymruScoutTopTagsByIP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutTopTagsByIP.yaml) | - | - |
| [CymruScoutWhois](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutWhois.yaml) | - | - |
| [CymruScoutX509Data](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Parsers/CymruScoutX509Data.yaml) | - | - |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [TeamCymruScoutDomainData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Watchlists/TeamCymruScoutDomainData.json) | - | - |
| [TeamCymruScoutIPData](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Team%20Cymru%20Scout/Watchlists/TeamCymruScoutIPData.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.1.1       | 25-09-2025                     | Fixed bug in TeamCymruScoutEnrichIncident playbook. |
| 3.1.0       | 16-05-2025                     | Updated Workbook, Parser, Data Connector and created new playbook. |
| 3.0.0       | 07-08-2024                     | Added Solution for Team Cymru Scout. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
