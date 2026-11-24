# Changelog for ASimAlertEventCrowdStrikeFalcon.yaml

## Version 1.0.0

- (2026-11-23) Set the ingestion-time parser version to 1.0.0 and standardize its display name; parser queries and normalization behavior are unchanged. - [PR #15727](https://github.com/Azure/Azure-Sentinel/pull/15727)
- Rename the display name to `CrowdStrikeDetections AlertEvent ASIM parser`.
- Align Change.Date with Parser.LastUpdated to satisfy static metadata validation.

## Version 0.1.3

- (2026-11-06) Restore InputStream to none for the CrowdStrike Falcon workspace ingestion-time parser - [PR #15588](https://github.com/Azure/Azure-Sentinel/pull/15588)

## Version 0.1.2

- (2026-11-06) Update the ingestion stream, emitted AlertEvent schema version, and indicator-type comparisons - [PR #15569](https://github.com/Azure/Azure-Sentinel/pull/15569)
- Set EventSchemaVersion to 1.0.0 and convert IOC type values to strings before comparison.
