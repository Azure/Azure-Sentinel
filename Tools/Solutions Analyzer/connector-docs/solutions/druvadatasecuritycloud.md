# DruvaDataSecurityCloud

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Druva Inc |
| **Support Tier** | Partner |
| **Support Link** | [https://support.druva.com/](https://support.druva.com/) |
| **Categories** | domains |
| **First Published** | 2024-12-24 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Druva Events Connector](../connectors/druvaeventccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DruvaInsyncEvents_CL`](../tables/druvainsyncevents-cl.md) | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) | - |
| [`DruvaPlatformEvents_CL`](../tables/druvaplatformevents-cl.md) | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) | - |
| [`DruvaSecurityEvents_CL`](../tables/druvasecurityevents-cl.md) | [Druva Events Connector](../connectors/druvaeventccpdefinition.md) | - |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 5 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Druva Quarantine Playbook for Enterprise Workload](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Playbooks/DruvaQuarantineEnterpriseWorkload/azuredeploy.json) | This playbook uses Druva-Ransomware-Response capabilities to stop the spread of ransomware and avoid... | - |
| [Druva Quarantine Playbook for Shared Drive](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Playbooks/DruvaQuarantineSharedDrive/azuredeploy.json) | This playbook uses Druva-Ransomware-Response capabilities to stop the spread of ransomware and avoid... | - |
| [Druva Quarantine Playbook for Sharepoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Playbooks/DruvaQuarantineSharePoint/azuredeploy.json) | This playbook uses Druva-Ransomware-Response capabilities to stop the spread of ransomware and avoid... | - |
| [Druva Quarantine Playbook for inSync Workloads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Playbooks/DruvaQuarantineInsyncWorkloads/azuredeploy.json) | This playbook uses Druva-Ransomware-Response capabilities to stop the spread of ransomware and avoid... | - |
| [Druva Quarantine Using Resource id](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DruvaDataSecurityCloud/Playbooks/DruvaQuarantineUsingResourceID/azuredeploy.json) | This playbook uses Druva-Ransomware-Response capabilities to stop the spread of ransomware and avoid... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
| 3.0.0       | 09-01-2025                     | Initial Solution Release                               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
