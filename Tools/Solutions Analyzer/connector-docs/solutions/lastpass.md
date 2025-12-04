# LastPass

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | The Collective Consulting |
| **Support Tier** | Partner |
| **Support Link** | [https://thecollective.eu](https://thecollective.eu) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Last Updated** | 2022-01-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### LastPass Enterprise - Reporting (Polling CCP)

**Publisher:** The Collective Consulting BV

The [LastPass Enterprise](https://www.lastpass.com/products/enterprise-password-management-and-sso) connector provides the capability to LastPass reporting (audit) logs into Microsoft Sentinel. The connector provides visibility into logins and activity within LastPass (such as reading and removing passwords).

**Tables Ingested:**

- `LastPassNativePoller_CL`

**Connector Definition Files:**

- [LastPassAPIConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Data%20Connectors/LastPassAPIConnector.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `LastPassNativePoller_CL` | LastPass Enterprise - Reporting (Polling CCP) |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n