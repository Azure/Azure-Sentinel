# SIGNL4

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Derdack |
| **Support Tier** | Partner |
| **Support Link** | [https://www.signl4.com](https://www.signl4.com) |
| **Categories** | domains |
| **First Published** | 2021-12-10 |
| **Last Updated** | 2021-12-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SIGNL4](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SIGNL4) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Derdack SIGNL4](../connectors/derdacksignl4.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SIGNL4_CL`](../tables/signl4-cl.md) | [Derdack SIGNL4](../connectors/derdacksignl4.md) | - |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityIncident`](../tables/securityincident.md) | [Derdack SIGNL4](../connectors/derdacksignl4.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 1 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [SIGNL4 Alerting and Response](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SIGNL4/Playbooks/SIGNL4_Alerting_and_Response/azuredeploy.json) | This playbook will be sending alerts with basic incidents to SIGNL4 teams when an incident is create... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                           |
|-------------|--------------------------------|------------------------------------------------------------------------------|
| 3.0.0       | 02-06-2025                     | This version introduces several updates to the SIGNL4 solution for Microsoft Sentinel, focusing on improving metadata, updating templates, and enhancing descriptions for better clarity and functionality.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
