# Manage VIP monitoring

The Microsoft Exchange Security solutions use Microsoft Sentinel watchlists to identify activity that affects VIP users. VIP filters are available in:

- **Microsoft Exchange Admin Activity**
- **Microsoft Exchange Admin Activity - Online**

## Watchlists

| Solution | Display name | Alias | Required identity fields |
|----------|--------------|-------|--------------------------|
| Exchange On-Premises | Exchange VIP | `ExchangeVIP` | `displayName`, `userPrincipalName`, `sAMAccountName`, `objectSID`, `objectGUID`, `canonicalName`, `distinguishedName` |
| Exchange Online | Exchange Online VIP | `ExchOnlineVIP` | `displayName`, `sAMAccountName`, `userPrincipalName` |

The solution packages create these watchlists with sample rows. Replace the samples with the users that your organization classifies as VIPs.

## Configure VIP entries

1. In Microsoft Sentinel, open **Watchlist**.
2. Select the watchlist for the target Exchange solution.
3. Add or update entries without changing the column names.
4. Populate as many identity fields as possible so that workbook queries can match the different formats recorded in administrative events.
5. Save the watchlist and allow time for the changes to become available to queries.
6. Open the corresponding administrative activity workbook and enable its VIP filter.

Keep the watchlists current when VIP accounts are renamed, removed, or moved between environments.
