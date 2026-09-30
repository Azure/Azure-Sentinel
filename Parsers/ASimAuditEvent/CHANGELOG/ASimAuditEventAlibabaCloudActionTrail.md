# Changelog for ASimAuditEventAlibabaCloudActionTrail.yaml

## Version 0.1.0 - 2026-09-14

- (2026-09-14) Initial creation of the parser
- Normalizes Alibaba Cloud ActionTrail control-plane audit activity across all services except Ims, CloudSSO and Ram, which are covered by ASimUserManagementAlibabaCloudActionTrail
- Excludes AliyunServiceEvent entries (Alibaba's own service-linked principals acting on the tenant's behalf)
