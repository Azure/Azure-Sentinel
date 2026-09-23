## 3.0.0

**What's new**

- Unified `WhoisFreaks` KQL parser across all 7 custom tables
- Analytic rules: threat-domain match against DNS/proxy/email; NRD contact detection
- Hunting queries: TI↔DNS join, NRD↔proxy join, high-confidence threat list
- Overview workbook: volume, feed mix, top TLDs, NRD age, TI matches

**Ingestion fixes**

- Pagination uses pre-filter raw counts (no silent data loss on domain-list feeds)
- Logs Ingestion API payloads chunked under 1 MB
- `whois` query param sent as lowercase `true`/`false`
- Stale feed-lock recovery after crash
- Timer failures surface in App Insights

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
| --- | --- | --- |
| 3.0.0 | 21-09-2026 | Initial production-ready Microsoft Sentinel solution package. Azure Functions-based data connector for WhoisFreaks threat intelligence and newly registered domain (NRD) feeds. Deploys Function App (Linux Consumption), storage, Data Collection Endpoint, Data Collection Rule, and 7 custom Log Analytics tables via azuredeploy.json. Supports malware, phishing, spam, and NRD gTLD/ccTLD feeds (with/without WHOIS). Managed identity for storage and DCR ingestion. Content Hub package registers connector UI only; infrastructure is deployed via Deploy to Azure button. |
