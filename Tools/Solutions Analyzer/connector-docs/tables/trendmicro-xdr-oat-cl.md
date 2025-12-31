# TrendMicro_XDR_OAT_CL

## Solutions (4)

This table is used by the following solutions:

- [Endpoint Threat Protection Essentials](../solutions/endpoint-threat-protection-essentials.md)
- [Malware Protection Essentials](../solutions/malware-protection-essentials.md)
- [Microsoft Defender XDR](../solutions/microsoft-defender-xdr.md)
- [Trend Micro Vision One](../solutions/trend-micro-vision-one.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Trend Vision One](../connectors/trendmicroxdr.md)

---

## Content Items Using This Table (11)

### Analytic Rules (7)

**In solution [Malware Protection Essentials](../solutions/malware-protection-essentials.md):**
- [Detect Malicious Usage of Recovery Tools to Delete Backup Files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/BackupDeletionDetected.yaml)
- [Detect Print Processors Registry Driver Key Creation/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/PrintProcessersModified.yaml)
- [Detect Registry Run Key Creation/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/StartupRegistryModified.yaml)
- [Detect Windows Allow Firewall Rule Addition/Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/WindowsAllowFirewallRuleAdded.yaml)
- [Detect Windows Update Disabled from Registry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Malware%20Protection%20Essentials/Analytic%20Rules/WindowsUpdateDisabled.yaml)
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

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
