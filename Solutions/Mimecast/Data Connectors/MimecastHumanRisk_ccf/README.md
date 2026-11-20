# Mimecast Human Risk (CCF)

Codeless Connector Framework (CCF) data connector for the [Mimecast Human Risk API](https://developer.services.mimecast.com/docs/human-risk/1/overview).
One Connect deploys four `RestApiPoller` rules that share a single OAuth 2.0 client-credentials configuration.

| Poller | Endpoint | Table | Events path |
|---|---|---|---|
| Organization | `GET /human-risk/v1/organization` (`monthsBack` = user setting, `fields=attackTotal,riskResponses,totals.*`) | `MimecastHumanRisk_Organization_CL` | `$.trends[*]` and `$.totals` |
| Behaviors | `GET /human-risk/v1/organization/behaviors` (`monthsBack` = user setting, `fields=events`) | `MimecastHumanRisk_Behaviors_CL` | `$.behaviors[*]` |
| Attacks | `GET /human-risk/v1/organization/attacks` (`monthsBack` = user setting, `fields=attackTypes`) | `MimecastHumanRisk_Attacks_CL` | `$` |
| Individuals | `POST /human-risk/v1/individuals/search` (no filter: all individuals, `pageSize=1000`, all optional fields) | `MimecastHumanRisk_Individuals_CL` | `$.individuals[*]` |

## Prerequisites
- A Mimecast API 2.0 application (Client ID / Client Secret) with the **Human Risk READ** permission.
- Your regional API base URL: `https://api.services.mimecast.com` (global), `https://uk-api.services.mimecast.com` or `https://us-api.services.mimecast.com` (no trailing slash).

## Configuration (connector page)
- **Mimecast API Base URL**, **Client ID**, **Client Secret**: required.
- **Months of data to request**: whole number 1-12 (default 3). Applied as `monthsBack` to the three organization endpoints. Not used by the individuals search.
- **Polling interval**: dropdown (1, 4, 8, 12, 24, 48 hours, 7 days; default 12 hours). Applied as `queryWindowInMin` to all pollers.

## Behavior notes
- The API has no event timestamps or time-window parameters. Each poll writes a snapshot and `TimeGenerated` is the ingestion time. Use `arg_max(TimeGenerated, *)` to get the latest snapshot (see the connector sample queries and the workbook).
- The organization response holds the monthly rows under `trends` and one aggregate `totals` object. Both land in `MimecastHumanRisk_Organization_CL`; the totals row has an empty `Month`.
- Individuals are paged with `meta.nextPage` -> `pageToken`. The request body is an empty `{}` (no filters, default sort `humanRiskScore:desc`), so every individual is ingested. Add a `filters` object to `queryParametersTemplate` in `MimecastHumanRisk_PollerConfig.json` to narrow it.
- Rate limits (per tenant): organization endpoints 10 RPS / 120 req/min, individuals search 2 RPS / 30 req/min. Pollers use `rateLimitQPS: 1`.

## Files
- `Data Connectors/MimecastHumanRisk_ccf/` - connector definition (UI), DCR, tables, pollers.
- Package with `Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1`.
