# Migration evidence — PaloAltoPrismaCloud

Solution: **PaloAltoPrismaCloud**
Run: `20261029T111422Z-d213dfe615544a50b23b4e208945fb34`
Profile: **qualification**
Recorded workflow status: **completed**
Current solution version at export: **3.2.2** (not a packaging claim)
Requested version action: **none**
Requested target solution version: **unknown (not recorded)** (not a packaged version)
Evidence exported at (UTC): **2026-10-29T14:40:55.110960+00:00**
Evidence exporter: **sentinel-xdr-migration 0.1.0** (export tool, not historical run version)
Exporter Python: **3.12.10**

**This is a local, curated snapshot, not trusted attestation or a new test run.**
Reported passes are not independently verified. Missing evidence is not a pass.
Content hashes describe export-time bytes, not proof of what historical tests ran.

## All workflow stages

| Stage | Recorded status | Attempts |
| --- | --- | --- |
| discovery | passed | 1 |
| conversion | passed | 1 |
| validation | passed | 1 |
| packaging | passed | 8 |
| deployment | passed | 1 |
| mockIngestion | passed | 1 |
| alertParity | passed | 1 |
| report | passed | 1 |

## Evidence coverage

| Report | Availability | Recorded status | Items | Recorded item outcomes |
| --- | --- | --- | --- | --- |
| conversion | available | unknown | 11 | converted=11 |
| structural | missing | unknown | 0 | not-recorded |
| runtimeGraph | available | unknown | 11 | passed=11; query hashes: matches=10, stale-or-missing=1 |
| runtimeTriage | missing | unknown | 0 | not-recorded |
| runtimeLogAnalytics | missing | unknown | 0 | not-recorded |
| runtimeAzureMonitorSdk | available | unknown | 11 | passed=11; query hashes: matches=10, stale-or-missing=1 |
| packaging | available | passed | 0 | not-recorded |
| queryParity | available | passed | 11 | passed=11 |
| alertParity | available | passed | 11 | passed=11 |
| solutionReport | available | unknown | 11 | structural: passed=11 |

See `evidence.json` for every result (including failures, blocks and not-run),
relative paths, hashes, version decisions and provenance mismatches.

Source-query provenance mismatches detected: **0**.
Missing/unsupported provenance remains unverified, even when this count is zero.

## Limitations

- Raw messages, provider records, alerts, credentials and lab identities are omitted.
- Historical commands/tool versions and baseline decisions have no supported persisted contract.
- New runtime reports bind results to the exact source or Advanced Hunting query hash; legacy or mismatched hashes are stale/unbound. Hashes do not attest that a provider executed the query.
- Unknown fields/statuses are excluded or marked unknown, never interpreted as success.
- This directory is never read as workflow state or included in Marketplace packages.
