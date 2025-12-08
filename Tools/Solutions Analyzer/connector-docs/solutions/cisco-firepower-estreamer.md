# Cisco Firepower EStreamer

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cisco |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cisco.com/c/en_in/support/index.html](https://www.cisco.com/c/en_in/support/index.html) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](../connectors/ciscofirepowerestreamer.md)

**Publisher:** Cisco

### [[Deprecated] Cisco Firepower eStreamer via AMA](../connectors/ciscofirepowerestreamerama.md)

**Publisher:** Cisco

eStreamer is a Client Server API designed for the Cisco Firepower NGFW Solution. The eStreamer client requests detailed event data on behalf of the SIEM or logging solution in the Common Event Format (CEF).

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CiscoFirepowerEStreamerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Data%20Connectors/template_CiscoFirepowerEStreamerAMA.json) |

[→ View full connector details](../connectors/ciscofirepowerestreamerama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Cisco Firepower eStreamer via AMA](../connectors/ciscofirepowerestreamerama.md), [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](../connectors/ciscofirepowerestreamer.md) |

[← Back to Solutions Index](../solutions-index.md)
