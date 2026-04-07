# Holm Security Solution Release Notes

## Version 3.0.0 (2026-03-30)

### New Features
- Initial release of the Holm Security CCF (Codeless Connector Framework) data connector for Microsoft Sentinel
- Ingests **network assets** from the Holm Security VMP API into the `net_assets_CL` Log Analytics table
- Ingests **web assets** from the Holm Security VMP API into the `web_assets_CL` Log Analytics table
- Supports pagination via offset/limit for large asset inventories
- Daily polling (once per 24 hours) to keep asset data current
- Configurable API base URL to support multiple Holm Security data center regions