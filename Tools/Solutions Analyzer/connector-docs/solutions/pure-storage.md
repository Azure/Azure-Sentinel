# Pure Storage

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | purestoragemarketplaceadmin |
| **Support Tier** | Partner |
| **Support Link** | [https://support.purestorage.com](https://support.purestorage.com) |
| **Categories** | domains |
| **First Published** | 2024-02-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Tables Reference

This solution queries **1 table(s)** from its content items:

| Table | Used By Content |
|-------|----------------|
| [`Syslog`](../tables/syslog.md) | Analytics |

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 4 |
| Analytic Rules | 3 |
| Parsers | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [External Fabric Module XFM1 is unhealthy](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Analytic%20Rules/FB-FabricModuleUnhealthy.yaml) | High | Execution | [`Syslog`](../tables/syslog.md) |
| [Pure Controller Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Analytic%20Rules/PureControllerFailed.yaml) | High | Execution | [`Syslog`](../tables/syslog.md) |
| [Pure Failed Login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Analytic%20Rules/PureFailedLogin.yaml) | High | CredentialAccess | [`Syslog`](../tables/syslog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Pure Storage FlashBlade File System Snapshot](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Playbooks/Pure-Storage-FlashBlade-File-System-Snapshot/azuredeploy.json) | This playbook gets triggered when a Microsoft Sentinel Incident created for suspicious activity and ... | - |
| [Pure Storage Protection Group Snapshot](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Playbooks/Pure-Storage-Protection-Groups-Snapshot/azuredeploy.json) | This playbook gets triggered when a Microsoft Sentinel Incident created for suspicious activity and ... | - |
| [Pure Storage User Deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Playbooks/Pure-Storage-User-Delete/azuredeploy.json) | This playbook gets triggered when a Microsoft Sentinel Incident created for suspicious user activity... | - |
| [Pure Storage Volume Snapshot](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Playbooks/Pure-Storage-Volumes-Snapshot/azuredeploy.json) | This playbook gets triggered when a Microsoft Sentinel Incident created for suspicious activity and ... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [PureStorageFlashArrayParser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Parsers/PureStorageFlashArrayParser.yaml) | - | - |
| [PureStorageFlashBladeParser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pure%20Storage/Parsers/PureStorageFlashBladeParser.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**             |
|-------------|--------------------------------|--------------------------------|
| 3.0.3       | 05-11-2024                     | Added new **Analytic Rule** a **Playbook** and a **Parser** |
| 3.0.2       | 09-05-2024                     | Repackaged for **Parser** issue fix on reinstall |
| 3.0.1       | 03-05-2024                     | Repackaged for **Parser** issue fix on reinstall<br/> Added 2 new **Analytic Rules** and 3 new **Playbooks** |
| 3.0.0       | 05-02-2024                     | Initial Solution Release - **Parser** Only   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
