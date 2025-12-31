# Armis

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Armis Corporation |
| **Support Tier** | Partner |
| **Support Link** | [https://support.armis.com/](https://support.armis.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-02 |
| **Last Updated** | 2024-08-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis) |

## Data Connectors

This solution provides **4 data connector(s)**:

- [Armis Activities](../connectors/armisactivities.md)
- [Armis Alerts](../connectors/armisalerts.md)
- [Armis Alerts Activities](../connectors/armisalertsactivities.md)
- [Armis Devices](../connectors/armisdevices.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Armis_Activities_CL`](../tables/armis-activities-cl.md) | [Armis Activities](../connectors/armisactivities.md), [Armis Alerts Activities](../connectors/armisalertsactivities.md) | - |
| [`Armis_Alerts_CL`](../tables/armis-alerts-cl.md) | [Armis Alerts](../connectors/armisalerts.md), [Armis Alerts Activities](../connectors/armisalertsactivities.md) | - |
| [`Armis_Devices_CL`](../tables/armis-devices-cl.md) | [Armis Devices](../connectors/armisdevices.md) | - |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 3 |
| Playbooks | 1 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Armis Update Alert Status](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Playbooks/ArmisUpdateAlertStatus/azuredeploy.json) | Armis Update Alert Status playbook would be responsible to update the Alert status from the sentinel... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ArmisActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Parsers/ArmisActivities.yaml) | - | - |
| [ArmisAlerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Parsers/ArmisAlerts.yaml) | - | - |
| [ArmisDevice](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Armis/Parsers/ArmisDevice.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.2.0       | 05-12-2025                     | Log Ingestion Support.|
| 3.1.1       | 19-05-2025                     | Updated Armis AlertActivity and Armis Device Data connectors to add keyvault for storing Armis Access Token and Severity parameter in AlertActivity.|
| 3.1.0       | 11-09-2024                     | Updated Armis Alerts Data connector to ingest Armis Activities associated with only Armis Alerts.|
| 3.0.3       | 26-08-2024                     | Updated the python runtime version to **3.11**|
| 3.0.2       | 03-05-2024                     | Repackaged for parser issue fix on reinstall|
| 3.0.1       | 15-04-2024                     | Added Deploy to Azure Government button in **Data connectors**|
| 3.0.0       | 03-11-2023                     | Fixed vulnerability related issue by passing the scret key in the body of the request instead of the param in the data connector and playbook        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
