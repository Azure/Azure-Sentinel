# CoreAzureBackup

Reference for CoreAzureBackup table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Azure Resources, IT & Management Tools |
| **Basic Logs Eligible** | ✗ No |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/coreazurebackup) |

## Solutions (1)

This table is used by the following solutions:

- [Microsoft Defender for Cloud](../solutions/microsoft-defender-for-cloud.md)

---

## Content Items Using This Table (1)

### Analytic Rules (1)

**In solution [Microsoft Defender for Cloud](../solutions/microsoft-defender-for-cloud.md):**
- [Detect CoreBackUp Deletion Activity from related Security Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Analytic%20Rules/CoreBackupDeletionwithSecurityAlert.yaml)

## Resource Types

This table collects data from the following Azure resource types:

- `microsoft.recoveryservices/vaults`

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
