# CyberArk Enterprise Password Vault (EPV) Events

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cyberark |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support/](https://www.cyberark.com/services-support/technical-support/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] CyberArk Enterprise Password Vault (EPV) Events via Legacy Agent](../connectors/cyberark.md)
- [[Deprecated] CyberArk Privilege Access Manager (PAM) Events via AMA](../connectors/cyberarkama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] CyberArk Enterprise Password Vault (EPV) Events via Legacy Agent](../connectors/cyberark.md), [[Deprecated] CyberArk Privilege Access Manager (PAM) Events via AMA](../connectors/cyberarkama.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CyberArkEPV](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Workbooks/CyberArkEPV.json) | [`CommonSecurityLog`](../tables/commonsecuritylog.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                         |
|-------------|--------------------------------|--------------------------------------------------------------------------------------------|
| 3.0.3       | 29-11-2024                     | Removed Deprecated **Data Connectors**   	                                                |
| 3.0.2       | 11-07-2024                     | Deprecating **data connectors**                                                            |           
| 3.0.1       | 06-03-2024                     | Internal terminology changes  																|
| 3.0.0       | 21-09-2023                     | Addition of new CyberArk Enterprise Password Vault (EPV) Events AMA **Data Connector**  	|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
