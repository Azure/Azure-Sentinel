# AADNonInteractiveUserSignInLogs

Reference for AADNonInteractiveUserSignInLogs table in Azure Monitor Logs.

| Attribute | Value |
|:----------|:------|
| **Category** | Entra |
| **Basic Logs Eligible** | ✓ Yes |
| **Supports Transformations** | ✓ Yes |
| **Ingestion API Supported** | ✗ No |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadnoninteractiveusersigninlogs) |

## Solutions (3)

This table is used by the following solutions:

- [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md)
- [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md)
- [Microsoft Entra ID](../solutions/microsoft-entra-id.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Microsoft Entra ID](../connectors/azureactivedirectory.md)

---

## Content Items Using This Table (4)

### Analytic Rules (3)

**In solution [Apache Log4j Vulnerability Detection](../solutions/apache-log4j-vulnerability-detection.md):**
- [Log4j vulnerability exploit aka Log4Shell IP IOC](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Apache%20Log4j%20Vulnerability%20Detection/Analytic%20Rules/Log4J_IPIOC_Dec112021.yaml)

**In solution [Lumen Defender Threat Feed](../solutions/lumen-defender-threat-feed.md):**
- [Lumen TI IPAddress in IdentityLogonEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Lumen%20Defender%20Threat%20Feed/Analytic%20Rules/Lumen_IPEntity_IdentityLogonEvents.yaml)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [Password spray attack against Microsoft Entra ID Seamless SSO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Analytic%20Rules/SeamlessSSOPasswordSpray.yaml)

### Workbooks (1)

**In solution [Microsoft Entra ID](../solutions/microsoft-entra-id.md):**
- [AzureActiveDirectorySignins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Workbooks/AzureActiveDirectorySignins.json)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
