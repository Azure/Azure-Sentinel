# Darktrace

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Darktrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.darktrace.com/en/contact/](https://www.darktrace.com/en/contact/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Darktrace Connector for Microsoft Sentinel REST API](../connectors/darktracerestconnector.md)

**Publisher:** Darktrace

The Darktrace REST API connector pushes real-time events from Darktrace to Microsoft Sentinel and is designed to be used with the Darktrace Solution for Sentinel. The connector writes logs to a custom log table titled "darktrace_model_alerts_CL"; Model Breaches, AI Analyst Incidents, System Alerts and Email Alerts can be ingested - additional filters can be set up on the Darktrace System Configuration page. Data is pushed to Sentinel from Darktrace masters.

| | |
|--------------------------|---|
| **Tables Ingested** | `darktrace_model_alerts_CL` |
| **Connector Definition Files** | [DarktraceConnectorRESTAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace/Data%20Connectors/DarktraceConnectorRESTAPI.json) |

[→ View full connector details](../connectors/darktracerestconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `darktrace_model_alerts_CL` | [Darktrace Connector for Microsoft Sentinel REST API](../connectors/darktracerestconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
