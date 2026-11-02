# Changelog for ASimFileEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0

- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring FileEvent parser. - [PR #15514](https://github.com/Azure/Azure-Sentinel/pull/15514)
- Forward `disabled` and `pack`.
- Support RDA tables without `SalesforceDomain` or `Type`: leave domain-derived fields empty when the domain column is absent and use the source table name when `Type` is absent. - [PR #15514](https://github.com/Azure/Azure-Sentinel/pull/15514)
- Reference the FileEventStore API and retain the documented session security level when packing. Missing API-download filenames remain empty.
- Normalizes documented API_DOWNLOAD, UI_DOWNLOAD, PREVIEW, and UPLOAD actions. FileName is used without inventing a path; API_DOWNLOAD rows without FileName can produce an empty TargetFilePath and require review. Upload is mapped conservatively, and transfer success is not inferred.
