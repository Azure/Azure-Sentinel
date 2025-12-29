# SecurityEvent

| Attribute | Value |
|:----------|:------|
| **Table Name** | `SecurityEvent` |
| **Category** | Security |
| **Solutions Using Table** | 4 |
| **Connectors Ingesting** | 6 |
| **Basic Logs Eligible** | Partial support - data arriving from Log Analytics agent (MMA) or Azure Monitor Agent (AMA) is fully supported. Data arriving via Diagnostics Extension agent is collected though storage while this path isn't supported. |
| **Ingestion API Supported** | ✓ Yes |
| **Azure Monitor Docs** | [View Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityevent) |

⚠️ **Note:** This table name is unique to specific connectors.

---

## Solutions (4)

This table is used by the following solutions:

- [Cyborg Security HUNTER](../solutions/cyborg-security-hunter.md)
- [Microsoft Exchange Security - Exchange On-Premises](../solutions/microsoft-exchange-security---exchange-on-premises.md)
- [Semperis Directory Services Protector](../solutions/semperis-directory-services-protector.md)
- [Windows Security Events](../solutions/windows-security-events.md)

## Connectors (6)

This table is ingested by the following connectors:

- [Cyborg Security HUNTER Hunt Packages](../connectors/cyborgsecurity-hunter.md)
- [[Deprecated] Microsoft Exchange Logs and Events](../connectors/esi-exchangeadminauditlogevents.md)
- [ Microsoft Active-Directory Domain Controllers Security Event Logs](../connectors/esi-opt34domaincontrollerssecurityeventlogs.md)
- [Security Events via Legacy Agent](../connectors/securityevents.md)
- [Semperis Directory Services Protector](../connectors/semperisdsp.md)
- [Windows Security Events via AMA](../connectors/windowssecurityevents.md)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
