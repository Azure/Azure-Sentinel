# Cisco Secure Cloud Analytics

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Cisco Secure Cloud Analytics](../connectors/stealthwatch.md)

**Publisher:** Cisco

The [Cisco Secure Cloud Analytics](https://www.cisco.com/c/en/us/products/security/stealthwatch/index.html) data connector provides the capability to ingest [Cisco Secure Cloud Analytics events](https://www.cisco.com/c/dam/en/us/td/docs/security/stealthwatch/management_console/securit_events_alarm_categories/7_4_2_Security_Events_and_Alarm_Categories_DV_2_1.pdf) into Microsoft Sentinel. Refer to [Cisco Secure Cloud Analytics documentation](https://www.cisco.com/c/dam/en/us/td/docs/security/stealthwatch/system_installation_configuration/7_5_0_System_Configuration_Guide_DV_1_3.pdf) for more information.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Syslog` |
| **Connector Definition Files** | [Cisco_Stealthwatch_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics/Data%20Connectors/Cisco_Stealthwatch_syslog.json) |

[→ View full connector details](../connectors/stealthwatch.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Syslog` | [[Deprecated] Cisco Secure Cloud Analytics](../connectors/stealthwatch.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.2       | 20-12-2024                     |    Removed Deprecated **Data connector**                           |
| 3.0.1       | 23-07-2024                     |	Deprecating data connectors                                     | 
| 3.0.0       | 13-05-2024                     |	Changes for rebranding from Cisco Stealthwatch to Cisco Secure Cloud Analytics         |

[← Back to Solutions Index](../solutions-index.md)
