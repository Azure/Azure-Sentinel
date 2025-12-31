# ContrastADR

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Contrast Security |
| **Support Tier** | Partner |
| **Support Link** | [https://support.contrastsecurity.com/hc/en-us](https://support.contrastsecurity.com/hc/en-us) |
| **Categories** | domains |
| **First Published** | 2025-01-18 |
| **Last Updated** | 2025-01-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [ContrastADR](../connectors/contrastadr.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ContrastADRIncident_CL`](../tables/contrastadrincident-cl.md) | [ContrastADR](../connectors/contrastadr.md) | Analytics |
| [`ContrastADR_CL`](../tables/contrastadr-cl.md) | [ContrastADR](../connectors/contrastadr.md) | Analytics |

## Content Items

This solution includes **17 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 9 |
| Analytic Rules | 6 |
| Parsers | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Contrast ADR - DLP SQL Injection Correlation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Analytic%20Rules/Contrast_ADR_SQL_Injection_Alert_with_DLP_alerts.yaml) | High | InitialAccess, CredentialAccess, Collection, Exfiltration, CommandAndControl, Reconnaissance, CredentialAccess, LateralMovement, Discovery | [`ContrastADR_CL`](../tables/contrastadr-cl.md) |
| [Contrast ADR - EDR Alert Correlation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Analytic%20Rules/Contrast_ADR_Confirmed_EDR.yaml) | Medium | Execution, DefenseEvasion, InitialAccess, CommandAndControl | [`ContrastADRIncident_CL`](../tables/contrastadrincident-cl.md) |
| [Contrast ADR - Exploited Attack Event](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Analytic%20Rules/Contrast_ADR_Exploited_Attack_Event.yaml) | High | InitialAccess, Execution, DefenseEvasion, LateralMovement, CommandAndControl | [`ContrastADR_CL`](../tables/contrastadr-cl.md) |
| [Contrast ADR - Exploited Attack in Production](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Analytic%20Rules/Contrast_ADR_Exploited_Attack_Event_in_Production.yaml) | High | InitialAccess, Execution, DefenseEvasion, LateralMovement, CommandAndControl | [`ContrastADR_CL`](../tables/contrastadr-cl.md) |
| [Contrast ADR - Security Incident Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Analytic%20Rules/Contrast_Security_ADR_incident.yaml) | Medium | InitialAccess, DefenseEvasion, Discovery, CommandAndControl | [`ContrastADRIncident_CL`](../tables/contrastadrincident-cl.md) |
| [Contrast ADR - WAF Alert Correlation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Analytic%20Rules/Contrast_ADR_Confirmed_WAF.yaml) | Medium | InitialAccess, DefenseEvasion, CommandAndControl | [`ContrastADR_CL`](../tables/contrastadr-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ContrastADR_Command_Injection_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_Command_Injection_Workbook.json) | - |
| [ContrastADR_Cross_Site_Scripting_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_Cross_Site_Scripting_Workbook.json) | - |
| [ContrastADR_Expression_Language_Injection_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_Expression_Language_Injection_Workbook.json) | - |
| [ContrastADR_HTTP_Method_Tampering_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_HTTP_Method_Tampering_Workbook.json) | - |
| [ContrastADR_JNDI_Injection_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_JNDI_Injection_Workbook.json) | - |
| [ContrastADR_Path_Traversal_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_Path_Traversal_Workbook.json) | - |
| [ContrastADR_SQL_Injection_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_SQL_Injection_Workbook.json) | - |
| [ContrastADR_Untrusted_Deserialization_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_Untrusted_Deserialization_Workbook.json) | - |
| [ContrastADR_XML External_Entity_Injection_Injection_Workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Workbooks/ContrastADR_XML%20External_Entity_Injection_Injection_Workbook.json) | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Contrast_alert_event_parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Parsers/Contrast_alert_event_parser.yaml) | - | - |
| [Contrast_incident_parser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ContrastADR/Parsers/Contrast_incident_parser.yaml) | - | - |

## Release Notes

**Version** | **Date Modified (DD-MM-YYYY)** | **ChangeHistory**                               |
|------------|--------------------------------|-------------------------------------------------|
| 3.0.1      | 11-11-2025                     | Updated **Workbook** and parsing logic in both supported **Parsers** to improve accuracy and compatibility. |
| 3.0.0      | 22-02-2025                     | Initial Solution Release. |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
