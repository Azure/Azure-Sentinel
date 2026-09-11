# BitSight CCF ingestion deduplication investigation

## Status

The BitSight Codeless Connector Framework (CCF) connectors ingest unchanged
snapshot responses repeatedly. This is an ingestion-level duplication issue:
parser-level `arg_max()` can hide rows at query time, but cannot reduce stored
data, ingestion volume, or cost.

The current CCF `RestApiPoller` configuration cannot implement the legacy Azure
Functions connector's change-detection behavior. It has no durable,
per-entity content-state or content-hash facility. DCR transformations are
stateless and process each record independently; they cannot compare an
incoming record with a previous poll or maintain a hash cache.

## Azure Functions pattern

For a Company Details response, the legacy connector:

1. Retrieves the response for a company, such as company GUID `abc-123`.
2. Serializes the payload consistently and calculates a SHA-512 hash.
3. Reads the stored hash for `(CompanyDetails, abc-123)` from Azure Table
   Storage.
4. Sends the response to Log Analytics only when the hash differs.
5. Updates the stored hash after successful ingestion.

For company-scoped streams, the durable identity is the company GUID plus the
data type. The global vulnerabilities catalog is not company-scoped: its
identity is the vulnerability `Name`/CVE plus the data type.

## CCF behavior and limitation

The CCF snapshot collectors call BitSight endpoints on every poll and ingest
each response. The endpoints currently used by this solution do not provide an
`updated_since` filter, change cursor, ETag/conditional request, or equivalent
source-side change mechanism.

CCF checkpoint state tracks a time window or API pagination/cursor position; it
does not persist arbitrary per-entity response content. Adding a hash or
`CompanyGuid` column to a DCR does not make CCF able to suppress unchanged
records.

## Evidence in dhanu-la-prd

Workspace: `dhanu-la-prd` (West US 2)
Workspace ID: `3904e516-3461-4fce-8ad1-f702dfa70444`

Repeated identical payloads were measured after excluding `TimeGenerated` and
Log Analytics system metadata:

| Table | Duplicate rows |
|---|---:|
| `BitsightVulnerabilitiesFindingsSummary_CL` | 242,769,445 in the most recent seven days |
| `BitSightCompanyRatingDetails_CL` | 28,439 |
| `BitSightDiligenceStatistics_CL` | 16,125 |
| `BitSightFindingsSummary_CL` | 8,127 |
| `BitSightDiligenceHistoricalStatistics_CL` | 7,789 |
| `BitSightObservationStatistics_CL` | 6,787 |
| `BitsightIndustrialStatistics_CL` | 5,415 |
| `BitSightCompanyDetails_CL` | 31 |

`BitsightVulnerabilitiesFindingsSummary_CL` intentionally has no
`CompanyGuid`: it reads BitSight's global
`/customer-api/v1/defaults/vulnerabilities` catalog. It contains vulnerability
definitions, such as CVEs, rather than per-company data. Its correct business
identifier is `Name` (and `ConnectorName` when multiple connections exist).

## Source and deployment state

The parser-level deduplication added in PR #14800 was removed from:

- `Parsers/BitSightDiligenceStatistics.yaml`
- `Parsers/BitSightObservationStatistics.yaml`
- `Parsers/BitSightIndustrialStatistics.yaml`

This avoids presenting query-time deduplication as an ingestion fix. The
current BitSight 3.2.1 package was deployed to:

- Subscription: `ConnectorsAcceleration.Staging`
  (`2f0fdbc8-ab60-4386-af30-dd0fac77130e`)
- Resource group: `dhanu-rg`
- Workspace: `dhanu-fr-central`
- Deployment: `bitsight-20260902`

The `BitSightStatisticsConnector` and `BitSightEventsConnector` definitions
were confirmed after deployment.

## Required next step

Ask the CCF owning/Scuba team whether an existing or preview capability can
provide durable, connection-scoped per-entity content-hash state before DCR
submission. It must support nested polling and update state only after
successful ingestion.

Without that capability, the viable ways to prevent ingestion duplicates are:

1. Retain or reintroduce the stateful Azure Functions connector.
2. Use a BitSight API-provided change cursor, updated-since filter, or ETag if
   BitSight introduces one that CCF can use.
3. Request a CCF product enhancement for durable content-hash deduplication.
