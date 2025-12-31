# OpenCTI

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-09-22 |
| **Last Updated** | 2022-09-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenCTI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenCTI) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 4 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Indicator - OpenCTI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenCTI/Playbooks/OpenCTIPlaybooks/OpenCTI-CreateIndicator/azuredeploy.json) | This playbook adds new indicator in OpenCTI based on the entities info present in Sentinel incident.... | - |
| [Entity (IP, URL, FileHash, Account, Host) Enrichment - OpenCTI](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenCTI/Playbooks/OpenCTIPlaybooks/OpenCTI-EnrichIncident/azuredeploy.json) | This playbook search in OpenCTI for indicatoes based on the entities (Account, Host, IP, FileHash, U... | - |
| [Read Stream- OpenCTI Indicators](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenCTI/Playbooks/OpenCTIPlaybooks/OpenCTI-GetIndicatorsStream/azuredeploy.json) | This playbook fetches indicators from OpenCTI and send to Sentinel. Supported types are Domain, File... | - |
| [Send to Security Graph API - Batch Import (OpenCTI)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/OpenCTI/Playbooks/OpenCTIPlaybooks/OpenCTI-ImportToSentinel/azuredeploy.json) | This playbook sends messages to Security GraphAPI in batches | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
