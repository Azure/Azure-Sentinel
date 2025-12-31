# ServiceNow TISC

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ServiceNow |
| **Support Tier** | Partner |
| **Support Link** | [https://support.servicenow.com/now](https://support.servicenow.com/now) |
| **Categories** | domains |
| **First Published** | 2025-01-15 |
| **Last Updated** | 2025-01-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **8 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 8 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Export Domain Entity to TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ExportToTISC/ServiceNowTISC-Export_Domain_Entity/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to export Domain indicators found in Microsoft Senti... | - |
| [Export Hash Entity to TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ExportToTISC/ServiceNowTISC-Export_Hash_Entity/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to export Hash indicators found in Microsoft Sentine... | - |
| [Export IP Entity to TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ExportToTISC/ServiceNowTISC-Export_IP_Entity/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to export IP indicators found in Microsoft Sentinel ... | - |
| [Export URL Entity to TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ExportToTISC/ServiceNowTISC-Export_URL_Entity/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to export URL indicators found in Microsoft Sentinel... | - |
| [Export all Incident Entities to TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ExportToTISC/ServiceNowTISC-Export_Incident_Entities/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to export IP, Domain, URL, and Hash indicators found... | - |
| [ServiceNow TISC Batch Indicator Uploader](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ImportFromTISC/ServiceNowTISC-Batch_Indicator_Uploader/azuredeploy.json) | This playbook will write indicators in batch to ThreatIntelligenceIndicator log analytics table. Thi... | - |
| [ServiceNow TISC Import Observables from TISC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/ImportFromTISC/ServiceNowTISC-Import_Observables_Batch/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to import IP, Domain, URL, and Hash observables from... | - |
| [ServiceNow TISC Incident Enrichment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow%20TISC/Playbooks/Enrichment/ServiceNowTISC-Incident_Enrichment/azuredeploy.json) | This playbook leverages the ServiceNow TISC API to enrich IP, Domain, URL, and Hash indicators found... | - |

## Additional Documentation

> 📄 *Source: [ServiceNow TISC/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ServiceNow TISC/README.md)*

## Introduction
 
 ServiceNow's Threat Intelligence Security Center (TISC) is an advanced security intelligence platform, and this solution integrates with Microsoft Sentinel to provide comprehensive threat detection, analysis, and response capabilities. This integration enables organizations to aggregate threat intelligence from multiple sources, automate security workflows, and enhance their overall security posture. The solution facilitates bi-directional data exchange between TISC and Microsoft Sentinel, allowing security teams to seamlessly share threat indicators and observables across both platforms. The integration supports incident enrichment workflows, enabling security analysts to make more informed decisions based on consolidated threat intelligence. Through custom connectors and playbooks, the solution streamlines security operations by automating threat data correlation, reducing manual effort, and accelerating incident response times. 
 
 ServiceNow TISC Azure Sentinel Solution enables a range of capabilities, listed as follows:
 - Import Observables from TISC  to the Sentinel Workspace (into the ThreatIntelligenceIndicator table)
 - Enirchment of Sentinel incidents by fetching all details of entities associated with the incident.
 - Export entities associated to a Sentinel incident to TISC

This solutions provides all the required playbooks, which the customers can deploy into their Sentinel Workspace.

## Prerequisites

### Solution Dependencies
The Threat Intelligence solution from Microsoft Sentinel Content Hub must be installed for indicators to be forwarded to Microsoft Sentinel ThreatIntelligenceIndicator log table.

### Roles and Permissions on Sentinel

Microsoft article that describes roles and permissions in Microsoft Sentinel Roles and permissions in [Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/roles)

### ServiceNow TISC API Access
This solution is shipped with a custom connector which connects with TISC APIs for data exchange with Sentinel. The custom connector requires a valid username and password for the ServiceNow instance. And the user that is being used for the custom connector should have the following role:
-  `sn_sec_tisc.api_azure_sentinel_solution`

## Custom Connector for TISC API

When installing the custom connector, make sure to provide valid ServiceNow instance URL in the configuration screen. 

Here are the list of components provided by the logic apps custom connector, which internally calls the TISC API. 

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <strong>Import Observables in Indicator STIX format</strong>
      </td>
      <td>
        Returns list of observables that matches with filtering criteria in format accepted by the <a href="https://learn.microsoft.com/en-us/azure/sentinel/upload-indicators-api">Microsoft Sentinel Upload Indicator connector</a>
      </td>
    </tr>

*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
| 3.0.0       | 15-01-2025                     | Initial Solution Release                               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
