# Release Notes

## v1.0.6

- Replaced ZIP-based repo download with targeted per-file downloads via raw GitHub URLs
- Pointed all URLs to official Azure/Azure-Sentinel repository (Solutions/Training path)
- Updated sourceId to match existing Content Hub solution for seamless upgrades

## v1.0.5

- Added Content Hub V3 contentPackages resource for install/update/uninstall lifecycle
- Added search keyword GUID for Content Hub discoverability
- Updated branding to Microsoft Sentinel
- Aligned ARM template contentVersion with solution metadata version

## v1.0.4

- Added XDR custom detection rules deployment via Automation runbook
- Support for User-Assigned Managed Identity and Service Principal authentication
- Conditional deployment of detection rules based on auth method

## v1.0.3

- Added Azure Automation-based telemetry ingestion via Logs Ingestion API
- Support for built-in and custom table CSV data loading
- Added DCR auto-provisioning for custom tables

## v1.0.2

- Added watchlist deployment (High Risk Apps)
- Added hunting queries (OAuth Applications, Solorigate Inventory Check)
- Added playbook (Get-GeoFromIpAndTagIncident)

## v1.0.1

- Added analytic rules (Solorigate Network Beacon, Disabled Account Sign-ins, Malicious Inbox Rule)
- Added Investigation Insights workbook

## v1.0.0

- Initial release with Log Analytics workspace provisioning
