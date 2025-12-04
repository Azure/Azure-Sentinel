# AI Analyst Darktrace

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Darktrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.darktrace.com/en/contact/](https://www.darktrace.com/en/contact/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] AI Analyst Darktrace via Legacy Agent](../connectors/darktrace.md)

**Publisher:** Darktrace

### [[Deprecated] AI Analyst Darktrace via AMA](../connectors/darktraceama.md)

**Publisher:** Darktrace

The Darktrace connector lets users connect Darktrace Model Breaches in real-time with Microsoft Sentinel, allowing creation of custom Dashboards, Workbooks, Notebooks and Custom Alerts to improve investigation.  Microsoft Sentinel's enhanced visibility into Darktrace logs enables monitoring and mitigation of security threats.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_AIA-DarktraceAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AI%20Analyst%20Darktrace/Data%20Connectors/template_AIA-DarktraceAMA.json) |

[→ View full connector details](../connectors/darktraceama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] AI Analyst Darktrace via AMA](../connectors/darktraceama.md), [[Deprecated] AI Analyst Darktrace via Legacy Agent](../connectors/darktrace.md) |

[← Back to Solutions Index](../solutions-index.md)
