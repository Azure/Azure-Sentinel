# Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### [Deprecated] Fortinet FortiWeb Web Application Firewall via Legacy Agent

**Publisher:** Microsoft

The [fortiweb](https://www.fortinet.com/products/web-application-firewall/fortiweb) data connector provides the capability to ingest Threat Analytics and events into Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [Fortiweb.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/Fortiweb.json)

### Fortinet FortiWeb Web Application Firewall via AMA

**Publisher:** Microsoft

The [fortiweb](https://www.fortinet.com/products/web-application-firewall/fortiweb) data connector provides the capability to ingest Threat Analytics and events into Microsoft Sentinel.

**Tables Ingested:**

- `CommonSecurityLog`

**Connector Definition Files:**

- [template_FortiwebAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Fortinet%20FortiWeb%20Cloud%20WAF-as-a-Service%20connector%20for%20Microsoft%20Sentinel/Data%20Connectors/template_FortiwebAma.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | 2 connector(s) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n