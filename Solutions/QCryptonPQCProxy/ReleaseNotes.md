# QCrypton PQC Proxy for Microsoft Sentinel — Release Notes

## v3.0.0 (29-10-2026)

Initial release of the QCrypton PQC Proxy Sentinel Content Hub solution.

### Components

- **1 Data Connector** — Codeless Connector Framework (RestApiPoller) polling QCrypton API for proxy handshake telemetry
- **6 Analytic Rules:**
  - PQC downgrade detected — client offered hybrid but classical was negotiated (High)
  - PQC Proxy certificate expiring within 30 days (Medium)
  - PQC Proxy certificate expiring within 7 days — immediate renewal required (High)
  - TLS handshake failure spike on PQC Proxy (Medium)
  - Upstream backend connection failures on PQC Proxy (Medium)
  - High percentage of clients connecting without PQC support (Informational)
- **1 Workbook** — Hybrid Post-Quantum TLS Dashboard with adoption tracking, downgrade trends, certificate health, and per-proxy metrics
- **1 Playbook** — Teams notification on Sentinel incidents

### Custom Table

- **PQCProxy_CL** — TLS handshake telemetry including negotiated key exchange groups, PQC downgrade events, certificate health signals, and connection metrics

### Key Exchange Groups Tracked

- X25519MLKEM768 (hybrid post-quantum — preferred)
- X25519Kyber768Draft00 (hybrid post-quantum — legacy draft)
- X25519 (classical fallback)
- P-256 (classical fallback)
