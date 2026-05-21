# Changelog for vimAuthenticationVMwareVCenter.yaml

## Version 0.1.2

- (2026-05-01) Fix typing of DvcId from dynamic to string - [PR #14182](https://github.com/Azure/Azure-Sentinel/pull/14182)

## Version 0.1.1

- (2026-04-14) Add missing column EventSeverity - [PR #14075](https://github.com/Azure/Azure-Sentinel/pull/14075)
- Rename ActorUsername to TargetUsername
- Add alias User, which maps to TargetUsername
- Add post-filtering of TargetUsername
- Extract DvcId from Message
- Add alias Dvc, which maps to DvcId

## Version 0.1.0

- (2026-04-07) Create parser for VMware VCenter. Logs can come from on-premise VMs or Azure VMware instances. - [PR #13929](https://github.com/Azure/Azure-Sentinel/pull/13929)

