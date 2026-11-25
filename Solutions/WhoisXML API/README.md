# WhoisXML API solution for Microsoft Sentinel

This solution brings three WhoisXML API domain feeds into Microsoft Sentinel and matches them against your own DNS, web proxy, endpoint and email logs:

- **Newly Registered Domains 2.0** (NRD): domains registered in the last day or so.
- **Threat Intelligence**: domains WhoisXML API lists as malicious, with a threat type.
- **Bulk Registration Risk** (typosquatting): groups of similar domains that started to resolve on the same day.

It installs a codeless data connector, three custom tables, six analytics rules, three hunting queries, two example watchlists and a list of hosting platforms.

## Prerequisites

- A WhoisXML API key with a subscription to each feed you enable. For Newly Registered Domains 2.0, you also need to know your subscription tier (Lite, Basic, Professional, Enterprise or Ultimate).
- For the rules: the ASIM DNS and Web Session parsers, and Microsoft Defender XDR tables where you have them. Each rule uses only the log sources it names below.

## How the connector works

The connector polls WhoisXML API's feed service at `feeds-api.whoisxmlapi.com` once an hour per feed. Your API key travels in the `X-Api-Key` header. Before the service returns any rows, it checks your key with WhoisXML API's download server for the exact files those rows come from, so you receive only the feeds and tier your subscription includes. The service does not store your key.

Each feed is released once a day. Rows usually reach your tables 15 to 90 minutes after WhoisXML API releases them.

**IP allowlist.** If your WhoisXML API account restricts its API key to an IP allowlist, add the feed service's address to that allowlist before you connect. The connector page shows the address. Requests reach WhoisXML API from that address on your behalf, so once it is on your allowlist, anyone who holds your key can retrieve your feeds through this connector. Keep the key secret. WhoisXML API will tell you before the address changes. The feed service's public status page, `https://feeds-api.whoisxmlapi.com/v1/status`, lists the current addresses and the latest release of each feed.

## Connect, change or stop feeds

1. In Microsoft Sentinel, open **Data connectors**, then **WhoisXML API Domain Feeds (via Codeless Connector Framework)**.
2. Enter your API key, select the feeds your subscription includes and your Newly Registered Domains 2.0 tier, then select **Connect**.

The connector page does not read your feed and tier selections back after the page reloads. The **Data received** chart shows one line per feed. To change feeds or tier, or to stop a feed's ingestion, select **Disconnect**, change the selections, then select **Connect**. Disconnecting stops new rows; rows already ingested stay until their retention ends.

## Tables

`TimeGenerated` is the time a row was ingested, not a feed date. Azure Monitor replaces `TimeGenerated` values more than two days old with the time received, so the feed's own dates sit in their own columns. No table carries WHOIS contact or registrant fields.

**`WhoisXMLNRD_CL`** (retention 90 days)

| Column | Type | Meaning |
|---|---|---|
| TimeGenerated | datetime | Ingestion time |
| DomainName | string | Registered domain, lower-case, punycode for internationalized names |
| Reason | string | `added`, which WhoisXML API's NRD 2.0 specification defines as domains created in the last 24 hours plus those created in the last 7 days |
| FeedDate | datetime | Data day of the WhoisXML API file |
| Tier | string | NRD 2.0 tier the row was read from (`lite`, `basic`, `professional`, `enterprise`, `ultimate`) |

**`WhoisXMLThreatDomains_CL`** (retention 30 days)

| Column | Type | Meaning |
|---|---|---|
| TimeGenerated | datetime | Ingestion time |
| DomainName | string | Listed domain, lower-case |
| ThreatType | string | `attack`, `botnet`, `c2`, `malware`, `phishing`, `spam`, `suspicious`, `tor` or `generic` |
| FirstSeen | datetime | Day WhoisXML API first observed the domain |
| LastSeen | datetime | Day WhoisXML API last observed the domain, as of `FeedDate` |
| ChangeType | string | `added`, `removed` or `active` (see below) |
| FeedDate | datetime | Date of the snapshot the row was computed from |
| FeedVersion | int | Version of that day's file: 1, then 2 and up if WhoisXML API republishes it |
| ParentRank | int | Rank of the listing's registered domain in a public list of popular domains; 0 if unranked |
| IsPublicSuffix | bool | True when the listed domain is itself a public suffix, such as `mysynology.net` or `s3.amazonaws.com`, under which unrelated parties hold names |

**`WhoisXMLTyposquatting_CL`** (retention 90 days)

| Column | Type | Meaning |
|---|---|---|
| TimeGenerated | datetime | Ingestion time |
| DomainName | string | Domain, lower-case ASCII |
| DomainNameUtf | string | Unicode form of an internationalized domain name, else empty |
| GroupNumber | int | Group number within the day; a group is identified by `FeedDate` and `GroupNumber` |
| GroupMemberNumber | int | Position of the domain within its group |
| GroupSize | int | Number of domains in the group |
| FeedDate | datetime | Day the group's domains started to resolve in DNS |

Retention up to 90 days carries no extra charge in a Microsoft Sentinel workspace.

## What the dates mean

- **`FeedDate` is not the time a domain was listed.** For Newly Registered Domains 2.0 it is midnight UTC of the file's data day; the file is published about a day later. For Threat Intelligence it is the day of the snapshot. For Bulk Registration Risk it is the day the group's domains started to resolve.
- **`ListedInWorkspace`**, which the rules and hunting queries report, is the first `TimeGenerated` of a domain's rows in your workspace. For domains that arrived in the history sent after you first connect, it is the time that history arrived.
- **Lag.** For .com and .net, the median time from a domain's registration to its appearance in the Newly Registered Domains 2.0 file is about 23 hours, and the 90th percentile about 58 hours. A hostile domain is therefore often looked up before it is listed. The rules catch later lookups; the hunting query "DNS lookups that preceded a domain's listing as newly registered" finds earlier ones.

## Reading the Threat Intelligence table

The Threat Intelligence feed arrives as daily changes, not as the full list every day:

- `added`: the domain and threat type are in today's snapshot and were not in the previous one.
- `removed`: the domain and threat type were in the previous snapshot and are no longer listed. Log Analytics cannot delete rows, so a removal is a row of its own.
- `active`: the domain is still listed. Every listed domain is re-sent as `active` at least every 10 days, so the last 14 days of the table always hold the full list. After you first connect, the full list arrives as `active` rows over about the first 14 hours, unless another workspace already polls with your API key (see "History is kept per API key" below).

A change only to `LastSeen` produces no row on its own; the next `active` re-send carries the new value.

The current state of a domain is its newest row for that `DomainName` and `ThreatType`, ordered by `FeedDate` and then `FeedVersion`. It is listed unless that row's `ChangeType` is `removed`. Do not order by `TimeGenerated`: history rows from an older snapshot can arrive after newer changes.

```kusto
WhoisXMLThreatDomains_CL
| where TimeGenerated > ago(14d)
| extend StateKey = FeedDate + FeedVersion * 1s
| summarize arg_max(StateKey, *) by DomainName, ThreatType
| where ChangeType != "removed"
```

**What the Threat Intelligence feed does not tell you.** Listings carry a threat type but no confidence score and no source. A domain stays listed for up to 90 days after WhoisXML API last observed it. The rules therefore grade severity by threat type and by how recently the domain was seen:

- High for `c2`, `malware`, `phishing` or `botnet` listings seen in the last 14 days;
- Medium for any listing seen in the last 30 days;
- Low for older listings;
- Informational when the listing sits under a registered domain ranked in the top 100,000 popular domains (`ParentRank`), because hosts under popular services also appear in the feed.

A listed subdomain of a hosting platform in `WhoisXMLHostingPlatforms` or `WhoisXMLHostingPlatformsCustom` keeps its severity, because each subdomain there is a different party's site: free website hosts, site builders and dynamic DNS services such as `weebly.com`. The platform itself and its own `www` host stay Informational.

A listing matches the host itself and every host under it, except a listing that is itself a public suffix (`IsPublicSuffix`), which matches only a host with exactly that name: the hosts under `mysynology.net` belong to unrelated parties, not to whoever is listed.

## Ingestion cost and first-day history

These are estimates at the Microsoft Sentinel pay-as-you-go list price of $4.30 per GB (East US). Workspaces on a commitment tier pay less per GB, and other regions differ.

| Feed | Rows a day | GB a day | About a month |
|---|---|---|---|
| Newly Registered Domains 2.0, Lite, Basic or Professional | about 320,000 | 0.022 | $2.87 |
| Newly Registered Domains 2.0, Enterprise or Ultimate | about 450,000 | 0.031 | $4.08 |
| Threat Intelligence (about 6 million listed domains) | about 690,000 | 0.096 | $12.58 |
| Bulk Registration Risk | about 63,000 | 0.004 | $0.55 |

With all three feeds on, expect about 0.12 GB a day, roughly $16 a month, or about $20 if the Threat Intelligence list grows to 7 million domains. The Threat Intelligence feed is most of it.

**History on first connect.** So that the rules have something to match from the first day, the feed service sends history in hourly slices over the first day: the 7 newest days of Newly Registered Domains 2.0 for your tier and of Bulk Registration Risk (about 7 hours each), and the full Threat Intelligence list (about 14 hours). That is about 1 GB, roughly $4.40. If you disconnect and connect again within 7 days, you receive only what you missed; after 7 days or more, you receive the full history again. For Threat Intelligence the limit is 14 days, not 7: within 14 days you receive the changes you missed, removals included, and after 14 days or more the full list again. Choosing a different Newly Registered Domains 2.0 tier brings that tier's 7 days of history.

**Use a separate API key for each workspace.** History is kept per API key, not per workspace: the feed service tracks what it has sent for each API key, feed and tier, and cannot tell which workspace is polling. A workspace you connect with a key that another workspace already polls, such as a test workspace or one in another region, receives no history of its own, only what the service sends from then on; its Threat Intelligence list fills in over about 10 days as listed domains are re-sent. A workspace that disconnects and connects again while another workspace keeps polling with the same key does not receive what it missed, so for up to 14 days its Threat Intelligence rules can still match domains that were removed from the list in that time. If two workspaces share a key, an outage of more than about 30 minutes can also cost one of them a whole day's release while the other receives it, with no error in either. A workspace that polls with its own API key keeps its own history and is not affected. To have the history sent again for a key, contact WhoisXML API support. A workspace with its own key receives it again; on a shared key, a workspace may not receive the rows it missed, and may receive rows it already has.

To see your actual volume, run the connector's **Ingestion volume by table** sample query:

```kusto
union WhoisXMLNRD_CL, WhoisXMLThreatDomains_CL, WhoisXMLTyposquatting_CL
| where TimeGenerated > ago(7d)
| summarize GB = round(sum(_BilledSize) / 1e9, 3) by Type, bin(TimeGenerated, 1d)
```

## Watchlists: use your own lists, not the shipped ones

The rules read two kinds of list:

| Watchlist alias | Search key column | Holds | Installed by the solution |
|---|---|---|---|
| `WhoisXMLBrandKeywordsCustom` | `Keyword` | Your brand keywords, for the brand-lookalike rule and hunting query | No, you create it |
| `WhoisXMLDomainAllowlistCustom` | `Domain` | Domains every rule should ignore | No, you create it |
| `WhoisXMLHostingPlatformsCustom` | `Domain` | Hosting platforms you add, where each subdomain is a different party's site | No, you create it |
| `WhoisXMLBrandKeywords` | `Keyword` | Examples only (`examplebrand`, `examplebank`), which the rules ignore | Yes |
| `WhoisXMLDomainAllowlist` | `Domain` | Example only (`example.com`) | Yes |
| `WhoisXMLHostingPlatforms` | `Domain` | WhoisXML API's list of about 200 hosting platforms, such as `weebly.com` and `blogspot.com.ar` | Yes |

The solution redeploys `WhoisXMLBrandKeywords`, `WhoisXMLDomainAllowlist` and `WhoisXMLHostingPlatforms` on every install and update, which can reset any entries you add to them. Keep your entries in the `Custom` watchlists, which the solution never touches.

To create them, in Microsoft Sentinel open **Watchlists**, select **New**, and create:

1. **Alias** `WhoisXMLBrandKeywordsCustom`, from a CSV file whose first line is `Keyword`, one brand keyword per line, with **SearchKey** `Keyword`. Keywords shorter than 4 characters are ignored.
2. **Alias** `WhoisXMLDomainAllowlistCustom`, from a CSV file whose first line is `Domain`, one registered domain per line (for example `contoso.com`; write an internationalized domain in its `xn--` form), with **SearchKey** `Domain`.
3. **Alias** `WhoisXMLHostingPlatformsCustom`, from a CSV file whose first line is `Domain`, one platform domain of two to four labels per line (for example `example-sites.com` or `sites.example.co.uk`; write an internationalized domain in its `xn--` form, such as `xn--bcher-kva.com`), with **SearchKey** `Domain`. Where a platform sits inside a listed one, the more specific entry wins. The rules read up to 100,000 platforms from the two lists together. You need it only to add a platform the shipped list lacks.

The brand-lookalike rule raises nothing until `WhoisXMLBrandKeywordsCustom` has keywords.

## Analytics rules and hunting queries

All rules run hourly over the last 14 days of feed data, and incidents are grouped per domain per day.

**Saving a rule in a very large network.** Microsoft Sentinel runs a rule's query when you save it. Where the network looks up millions of distinct DNS names an hour, saving can report a timeout even though the rule was saved, so refresh the rule list before you save it again.

| Rule | Logs joined | Severity |
|---|---|---|
| WhoisXML API - Newly registered domain resolved by internal host | `_Im_Dns` | Medium; Low when 20 or more hosts resolved it. Once per domain per 7 days |
| WhoisXML API - Newly registered domain linked in delivered email | `EmailUrlInfo`, `EmailEvents` | Medium, once per message |
| WhoisXML API - User clicked link to newly registered domain | `UrlClickEvents` | High, once per user and domain per 7 days |
| WhoisXML API - Threat intelligence domain resolved by internal host | `_Im_Dns` | By threat type, recency and popularity (above) |
| WhoisXML API - Connection to threat intelligence domain from endpoint or proxy | `DeviceNetworkEvents`, `_Im_WebSession`, `CommonSecurityLog` | By threat type, recency and popularity (above) |
| WhoisXML API - Lookalike of your brand resolved by internal host | `_Im_Dns` and your brand keywords | High, once per domain per 7 days |

Hunting queries:

- WhoisXML API - DNS lookups that preceded a domain's listing as newly registered
- WhoisXML API - Lookalikes of your brand in the typosquatting feed
- WhoisXML API - Bulk registration groups resolved from your estate

## Monitoring the connector

Turn on Microsoft Sentinel health monitoring for your workspace. Codeless connectors then write to the `SentinelHealth` table: a status-change event when a feed starts or stops failing, repeated hourly while its status stays the same, and, for each hour with polling errors, a failure summary that includes the time period that was queried. An outage of an hour or two can leave only failure summaries, whose `Status` is `Informational`, so alert on both. This query adds the failure summaries to Microsoft's query for the latest failure per connector. Run it every hour with a 2-day look-back: **Lookup data from the last** in a Sentinel analytics rule, **Override query time range** in an Azure Monitor log search alert. It returns a row on every run while a connector's latest status is `Failure`:

```kusto
let failing = SentinelHealth
    | where TimeGenerated > ago(2d)
    | where OperationName == 'Data fetch status change'
    | where Status in ('Success', 'Failure')
    | summarize TimeGenerated = arg_max(TimeGenerated, *) by SentinelResourceName, SentinelResourceId
    | where Status == 'Failure';
let summaries = SentinelHealth
    | where TimeGenerated > ago(90m)
    | where ingestion_time() > ago(1h)
    | where OperationName == 'Data fetch failure summary';
union failing, summaries
```

After an outage, some rows can arrive more than once. The rules and hunting queries count each domain once; in your own queries, count domains with `dcount(DomainName)`.

Common failures:

- **Your key is not entitled to a feed or tier.** The feed's polls fail and `SentinelHealth` records it; Connect may also report it, naming the Newly Registered Domains 2.0 tier tested. Disconnect, select the feeds and tier your subscription includes, then Connect.
- **IP allowlist.** Add the feed service's address to your WhoisXML API allowlist (see "How the connector works").
- **No new rows for more than a day.** Check the feed's latest release on the status page above.

## Support

WhoisXML API, support@whoisxmlapi.com.
