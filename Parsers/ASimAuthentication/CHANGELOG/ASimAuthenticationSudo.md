# Changelog for ASimAuthenticationSudo.yaml

## Version 0.2.0
- (2026-01-26) [ASIM] Authentication - sudo Parser changes [PR #13529](https://github.com/Azure/Azure-Sentinel/pull/13529)
- Add normalization of `SeverityLevel` to `EventSeverity`
- Add mapping of `SeverityLevel` to `EventOriginalSeverity`
- Remove unnormalized columns
- Add mapping of `HostIP` to `SrcIpAddr`
- Add mapping of `ProcessName` (sudo) to `TargetAppName`, `Application`, `ActingAppName`
- Add mapping of `ProcessID` to `ActingAppId`
- Add Alias `Src`, `Dvc`, `IpAddr`
- Correct mapping of EventProduct to `Linux`
- Improve parser by removing code duplication
- Improve filtering process of vim* parser

## Version 0.1.2

- (2023-07-24) Fix-Authentication-Parsers - [PR #8615](https://github.com/Azure/Azure-Sentinel/pull/8615)

## Version 0.1.1

- (2023-01-21) add ASimAuthentication Parsers for syslog sshd, su and sudo - [PR #7098](https://github.com/Azure/Azure-Sentinel/pull/7098)

