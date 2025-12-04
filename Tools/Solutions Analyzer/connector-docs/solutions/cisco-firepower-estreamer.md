# Cisco Firepower EStreamer

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Cisco |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cisco.com/c/en_in/support/index.html](https://www.cisco.com/c/en_in/support/index.html) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Cisco Firepower eStreamer via Legacy Agent

**Publisher:** Cisco

eStreamer is a Client Server API designed for the Cisco Firepower NGFW Solution. The eStreamer client requests detailed event data on behalf of the SIEM or logging solution in the Common Event Format (CEF).

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [CiscoFirepowerEStreamerCollector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Data%20Connectors/CiscoFirepowerEStreamerCollector.json)

### [Deprecated] Cisco Firepower eStreamer via AMA

**Publisher:** Cisco

eStreamer is a Client Server API designed for the Cisco Firepower NGFW Solution. The eStreamer client requests detailed event data on behalf of the SIEM or logging solution in the Common Event Format (CEF).

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_CiscoFirepowerEStreamerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Data%20Connectors/template_CiscoFirepowerEStreamerAMA.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n