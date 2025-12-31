# Cisco Firepower EStreamer

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cisco |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cisco.com/c/en_in/support/index.html](https://www.cisco.com/c/en_in/support/index.html) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](../connectors/ciscofirepowerestreamer.md)
- [[Deprecated] Cisco Firepower eStreamer via AMA](../connectors/ciscofirepowerestreamerama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Cisco Firepower eStreamer via AMA](../connectors/ciscofirepowerestreamerama.md), [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](../connectors/ciscofirepowerestreamer.md) | - |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 4 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block IP - Cisco Firepower](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Playbooks/CiscoFirepower-BlockIP-NetworkGroup/azuredeploy.json) | This playbook allows blocking of IPs in Cisco Firepower, using a **Network Group object**. This allo... | - |
| [Block IP - Take Action from Teams - Cisco Firepower](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Playbooks/CiscoFirepower-BlockIP-Teams/azuredeploy.json) | This playbook allows blocking of IPs in Cisco Firepower, using a **Network Group object**. This allo... | - |
| [Block URL - Cisco Firepower](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Playbooks/CiscoFirepower-BlockFQDN-NetworkGroup/azuredeploy.json) | This playbook allows blocking of FQDNs in Cisco Firepower, using a **Network Group object**. This al... | - |
| [CiscoFirepower-swagger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Playbooks/CiscoFirepowerConnector/CiscoFirepower-swagger.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                  | 
|-------------|--------------------------------|---------------------------------------------------------------------|
| 3.0.1       | 10-07-2024                     |    Deprecating data connectors.                                     |
| 3.0.0       | 26-09-2023                     |	Addition of new Cisco Firepower EStreamer AMA **Data Connector** |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
