# LastPass

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | The Collective Consulting |
| **Support Tier** | Partner |
| **Support Link** | [https://thecollective.eu](https://thecollective.eu) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Last Updated** | 2022-01-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [LastPass Enterprise - Reporting (Polling CCP)](../connectors/lastpass-polling.md)

**Publisher:** The Collective Consulting BV

The [LastPass Enterprise](https://www.lastpass.com/products/enterprise-password-management-and-sso) connector provides the capability to LastPass reporting (audit) logs into Microsoft Sentinel. The connector provides visibility into logins and activity within LastPass (such as reading and removing passwords).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **LastPass API Key and CID**: A LastPass API key and CID are required. [See the documentation to learn more about LastPass API](https://support.logmeininc.com/lastpass/help/use-the-lastpass-provisioning-api-lp010068).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect LastPass Enterprise to Microsoft Sentinel**

Provide the LastPass Provisioning API Key.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `LastPassNativePoller_CL` |
| **Connector Definition Files** | [LastPassAPIConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/LastPass/Data%20Connectors/LastPassAPIConnector.json) |

[→ View full connector details](../connectors/lastpass-polling.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `LastPassNativePoller_CL` | [LastPass Enterprise - Reporting (Polling CCP)](../connectors/lastpass-polling.md) |

[← Back to Solutions Index](../solutions-index.md)
