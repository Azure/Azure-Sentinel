# Changelog for vimFileEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward all filtering and control parameters; filter raw usernames and filenames before normalization, and derived event types, IP addresses, and hostnames immediately after calculation.
- Reference the FileEventStore API, use the guaranteed `SalesforceDomain` column directly, and retain the documented session security level when packing. Missing API-download filenames remain empty.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring FileEvent parser.
- Normalizes documented API_DOWNLOAD, UI_DOWNLOAD, PREVIEW, and UPLOAD actions. FileName is used without inventing a path; API_DOWNLOAD rows without FileName can produce an empty TargetFilePath and require review. Upload is mapped conservatively, and transfer success is not inferred.
