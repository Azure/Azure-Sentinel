# ASimProcessEventLogs

Reference for ASimProcessEventLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Normalized |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/asimprocesseventlogs) |

## Solutions (5)

This table is used by the following solutions:

- [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md)
- [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [VMware Carbon Black Cloud](../solutions/vmware-carbon-black-cloud.md)

## Connectors (2)

This table is ingested by the following connectors:

- [CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3)](../connectors/crowdstrikereplicatorv2.md)
- [VMware Carbon Black Cloud via AWS S3](../connectors/carbonblackawss3.md)

---

## Content Items Using This Table (7)

### Analytic Rules (3)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect Malicious Usage of Recovery Tools to Delete Backup Files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/BackupDeletionDetected.yaml)
- [Process Creation with Suspicious CommandLine Arguments](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/SuspiciousProcessCreation.yaml)

**In solution [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md):**
- [Imminent Ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20XDR/Analytic%20Rules/Campaign/Macaw%20Ransomware/ImminentRansomware.yaml)

### Hunting Queries (3)

**In solution [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md):**
- [Certutil (LOLBins and LOLScripts, Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_CertutilLoLBins.yaml)
- [Windows System Shutdown/Reboot (Normalized Process Events)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Endpoint%20Threat%20Protection%20Essentials/Hunting%20Queries/ASimProcess_WindowsSystemShutdownReboot.yaml)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect New Scheduled Task Creation that Run Executables From Non-Standard Location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Hunting%20Queries/NewMaliciousScheduledTask.yaml)

### Workbooks (1)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [MalwareProtectionEssentialsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Workbooks/MalwareProtectionEssentialsWorkbook.json)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.securityinsights/processeventnormalized`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
