# Cyfirma Compromised Accounts

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-05-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CYFIRMA Compromised Accounts](../connectors/cyfirmacompromisedaccountsdataconnector.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyfirmaCompromisedAccounts_CL`](../tables/cyfirmacompromisedaccounts-cl.md) | [CYFIRMA Compromised Accounts](../connectors/cyfirmacompromisedaccountsdataconnector.md) | Analytics |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 3 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CYFIRMA - Compromised Employees Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts/Analytic%20Rules/CompromisedEmployeesRule.yaml) | High | CredentialAccess, InitialAccess, Persistence | [`CyfirmaCompromisedAccounts_CL`](../tables/cyfirmacompromisedaccounts-cl.md) |
| [CYFIRMA - Customer Accounts Leaks Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts/Analytic%20Rules/CustomerAccountsLeaksRule.yaml) | High | CredentialAccess, InitialAccess | [`CyfirmaCompromisedAccounts_CL`](../tables/cyfirmacompromisedaccounts-cl.md) |
| [CYFIRMA - Public Accounts Leaks Detection Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts/Analytic%20Rules/PublicAccountsLeaksRule.yaml) | High | CredentialAccess, InitialAccess, Discovery | [`CyfirmaCompromisedAccounts_CL`](../tables/cyfirmacompromisedaccounts-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.2       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.1       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.0       | 17-06-2025                     | Initial Solution Release.                                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
