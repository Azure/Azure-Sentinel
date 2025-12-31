# Digital Shadows

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Digital Shadows |
| **Support Tier** | Partner |
| **Support Link** | [https://www.digitalshadows.com/](https://www.digitalshadows.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Digital Shadows Searchlight](../connectors/digitalshadowssearchlightazurefunctions.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DigitalShadows_CL`](../tables/digitalshadows-cl.md) | [Digital Shadows Searchlight](../connectors/digitalshadowssearchlightazurefunctions.md) | Workbooks |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |
| Playbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Digital Shadows Incident Creation for exclude-app](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Analytic%20Rules/Digital_Shadows_incident_creation_exclude.yaml) | Medium | - | - |
| [Digital Shadows Incident Creation for include-app](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Analytic%20Rules/Digital_Shadows_incident_creation_include.yaml) | Medium | - | - |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [DigitalShadows](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Workbooks/DigitalShadows.json) | [`DigitalShadows_CL`](../tables/digitalshadows-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Digital Shadows Playbook to Update Incident Status](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Digital%20Shadows/Playbooks/DigitalShadowsPlaybooktoUpdateIncidentStatus/DigitalShadowsPlaybook-UpdateIncidentStatus.json) | This playbook will update the status of Microsoft Sentinel incidents to match the status of the aler... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.0       | 30-11-2023                     |  Added new Entity Mapping to **Analytic Rules**                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
