# MailRisk by Secure Practice

| | |
|----------|-------|
| **Connector ID** | `SecurePracticeMailRiskConnector` |
| **Publisher** | Secure Practice |
| **Tables Ingested** | [`MailRiskEventEmails_CL`](../tables-index.md#mailriskeventemails_cl) |
| **Used in Solutions** | [MailRisk](../solutions/mailrisk.md) |
| **Connector Definition Files** | [MailRisk_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailRisk/Data%20Connectors/MailRisk_CCP/MailRisk_ConnectorDefinition.json) |

The MailRisk by Secure Practice connector allows you to ingest email threat intelligence data from the MailRisk API into Microsoft Sentinel. This connector provides visibility into reported emails, risk assessments, and security events related to email threats.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **API credentials**: Your Secure Practice API key pair is also needed, which are created in the [settings in the admin portal](https://manage.securepractice.co/settings/security). Generate a new key pair with description `Microsoft Sentinel`.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Obtain Secure Practice API Credentials**

Log in to your Secure Practice account and generate an API Key and API Secret if you haven't already.

**2. Connect to MailRisk API**

Enter your Secure Practice API credentials below. The credentials will be securely stored and used to authenticate API requests.
- **API Key**: Enter your Secure Practice API Key
- **API Secret**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
