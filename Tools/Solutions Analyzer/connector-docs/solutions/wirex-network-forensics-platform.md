# WireX Network Forensics Platform

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | WireX Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://wirexsystems.com/contact-us/](https://wirexsystems.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WireX%20Network%20Forensics%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WireX%20Network%20Forensics%20Platform) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] WireX Network Forensics Platform via Legacy Agent](../connectors/wirex-systems-nfp.md)

**Publisher:** WireX_Systems

### [[Deprecated] WireX Network Forensics Platform via AMA](../connectors/wirex-systems-nfpama.md)

**Publisher:** WireX_Systems

The WireX Systems data connector allows security professional to integrate with Microsoft Sentinel to allow you to further enrich your forensics investigations; to not only encompass the contextual content offered by WireX but to analyze data from other sources, and to create custom dashboards to give the most complete picture during a forensic investigation and to create custom workflows.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_WireXsystemsNFPAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/WireX%20Network%20Forensics%20Platform/Data%20Connectors/template_WireXsystemsNFPAMA.json) |

[→ View full connector details](../connectors/wirex-systems-nfpama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] WireX Network Forensics Platform via AMA](../connectors/wirex-systems-nfpama.md), [[Deprecated] WireX Network Forensics Platform via Legacy Agent](../connectors/wirex-systems-nfp.md) |

[← Back to Solutions Index](../solutions-index.md)
