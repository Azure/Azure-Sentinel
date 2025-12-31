# ASimRegistryEventLogs

Reference for ASimRegistryEventLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Normalized |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/asimregistryeventlogs) |

## Solutions (3)

This table is used by the following solutions:

- [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [VMware Carbon Black Cloud](../solutions/vmware-carbon-black-cloud.md)

## Connectors (2)

This table is ingested by the following connectors:

- [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)
- [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md)

---

## Content Items Using This Table (5)

### Analytic Rules (4)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect Print Processors Registry Driver Key Creation/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/PrintProcessersModified.yaml)
- [Detect Registry Run Key Creation/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/StartupRegistryModified.yaml)
- [Detect Windows Allow Firewall Rule Addition/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/WindowsAllowFirewallRuleAdded.yaml)
- [Detect Windows Update Disabled from Registry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/WindowsUpdateDisabled.yaml)

### Workbooks (1)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/asimtables`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
