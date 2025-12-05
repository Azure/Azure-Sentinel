# Contrast Protect

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Contrast Protect |
| **Support Tier** | Partner |
| **Support Link** | [https://docs.contrastsecurity.com/](https://docs.contrastsecurity.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Contrast Protect via Legacy Agent](../connectors/contrastprotect.md)

**Publisher:** Contrast Security

### [[Deprecated] Contrast Protect via AMA](../connectors/contrastprotectama.md)

**Publisher:** Contrast Security

Contrast Protect mitigates security threats in production applications with runtime protection and observability.  Attack event results (blocked, probed, suspicious...) and other information can be sent to Microsoft Microsoft Sentinel to blend with security information from other systems.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ContrastProtectAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Contrast%20Protect/Data%20Connectors/template_ContrastProtectAMA.json) |

[→ View full connector details](../connectors/contrastprotectama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Contrast Protect via AMA](../connectors/contrastprotectama.md), [[Deprecated] Contrast Protect via Legacy Agent](../connectors/contrastprotect.md) |

[← Back to Solutions Index](../solutions-index.md)
