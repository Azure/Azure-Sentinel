# Changelog for vimAuthenticationCrowdStrikeFalconHost.yaml

## Version 0.1.2

- (2026-11-11) Correct authentication event timestamps and source IP mappings - [PR #15630](https://github.com/Azure/Azure-Sentinel/pull/15630)
- Derive `EventStartTime` from `ReceiptTime` as Unix time in milliseconds instead of `DeviceCustomDate1`; `EventEndTime` continues to use `EventStartTime`.
- Map `DestinationTranslatedAddress` to `SrcIpAddr` instead of `TargetIpAddr`, and expose the `Src` and `IpAddr` aliases instead of `Dst`.
- Remove `DvcIpAddr` and set `Dvc` to `EventProduct`.

## Version 0.1.1

- (2024-04-11) Authentication parser filter update - [PR #10243](https://github.com/Azure/Azure-Sentinel/pull/10243)
- Align `LogonMethod` enumerations with what is expected from schema
- Remove unnormalized columns

## Version 0.1.0

- (2023-11-03) ASIM Authentication schema parser with its sample and test data for CrowdStrikeFalconHost - [PR #9015](https://github.com/Azure/Azure-Sentinel/pull/9015)
