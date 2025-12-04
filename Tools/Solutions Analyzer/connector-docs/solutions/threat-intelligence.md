# Threat Intelligence

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence) |

## Data Connectors

This solution provides **5 data connector(s)**.

### [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md)

**Publisher:** Microsoft

### [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md)

**Publisher:** Microsoft

### [Threat Intelligence Platforms](../connectors/threatintelligence.md)

**Publisher:** Microsoft

### [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md)

**Publisher:** Microsoft

### [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md)

**Publisher:** Microsoft

Microsoft Sentinel offers a data plane API to bring in threat intelligence from your Threat Intelligence Platform (TIP), such as Threat Connect, Palo Alto Networks MineMeld, MISP, or other integrated applications. Threat indicators can include IP addresses, domains, URLs, file hashes and email addresses. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/p/?linkid=2269830&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

| | |
|--------------------------|---|
| **Tables Ingested** | `ThreatIntelligenceIndicator` |
| **Connector Definition Files** | [template_ThreatIntelligenceUploadIndicators.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligenceUploadIndicators.json) |
| | [template_ThreatIntelligenceUploadIndicators_ForGov.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Threat%20Intelligence/Data%20Connectors/template_ThreatIntelligenceUploadIndicators_ForGov.json) |

[→ View full connector details](../connectors/threatintelligenceuploadindicatorsapi.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [Threat Intelligence Platforms](../connectors/threatintelligence.md) |
| `ThreatIntelligenceIndicator` | [Microsoft Defender Threat Intelligence](../connectors/microsoftdefenderthreatintelligence.md), [Premium Microsoft Defender Threat Intelligence](../connectors/premiummicrosoftdefenderforthreatintelligence.md), [Threat Intelligence Platforms](../connectors/threatintelligence.md), [Threat Intelligence Upload API (Preview)](../connectors/threatintelligenceuploadindicatorsapi.md), [Threat intelligence - TAXII](../connectors/threatintelligencetaxii.md) |

[← Back to Solutions Index](../solutions-index.md)
