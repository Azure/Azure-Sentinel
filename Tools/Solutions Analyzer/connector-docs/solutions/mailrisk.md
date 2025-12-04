# MailRisk

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Secure Practice |
| **Support Tier** | Partner |
| **Support Link** | [https://securepractice.co/support](https://securepractice.co/support) |
| **Categories** | domains |
| **First Published** | 2023-03-16 |
| **Last Updated** | 2025-10-27 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailRisk](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailRisk) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [MailRisk by Secure Practice](../connectors/securepracticemailriskconnector.md)

**Publisher:** Secure Practice

The MailRisk by Secure Practice connector allows you to ingest email threat intelligence data from the MailRisk API into Microsoft Sentinel. This connector provides visibility into reported emails, risk assessments, and security events related to email threats.

| | |
|--------------------------|---|
| **Tables Ingested** | `MailRiskEventEmails_CL` |
| **Connector Definition Files** | [MailRisk_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MailRisk/Data%20Connectors/MailRisk_CCP/MailRisk_ConnectorDefinition.json) |

[→ View full connector details](../connectors/securepracticemailriskconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MailRiskEventEmails_CL` | [MailRisk by Secure Practice](../connectors/securepracticemailriskconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
