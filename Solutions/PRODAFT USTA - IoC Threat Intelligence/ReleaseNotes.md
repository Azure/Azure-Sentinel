# PRODAFT USTA - IoC Threat Intelligence — Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.0       | 08-07-2026                     | Initial Solution Release. Ingests PRODAFT USTA indicators of compromise (malicious URLs, malware hashes, phishing sites) into Microsoft Sentinel Threat Intelligence as STIX 2.1 indicators via the Upload STIX Objects API. Three **import Playbooks** (one per IoC feed, hourly, managed-identity), three on-demand **backfill Playbooks** (one per feed, 90 days by default), a **Data Connector** card, three **Analytic Rules** (TI-map URL/Domain/File-hash against the `ThreatIntelIndicators` table), and an overview **Workbook**. |
