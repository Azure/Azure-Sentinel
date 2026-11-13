# QCrypton PQC Engine for Microsoft Sentinel — Release Notes

## v1.0.0 (01-11-2026)

Initial release of the QCrypton PQC Engine Sentinel Content Hub solution.

### Components

- **1 Data Connector** — Codeless Connector Framework (RestApiPoller) polling QCrypton API for PQC Engine runtime telemetry
- **6 Analytic Rules:**
  - PQC Engine policy blocked a TLS handshake (High)
  - Vulnerable classical algorithm detected in TLS negotiation (High)
  - PQC downgrade on engine — client offered hybrid but classical negotiated (High)
  - High percentage of classical-only clients on PQC Engine (Informational)
  - KEM operation failure spike on PQC Engine (Medium)
  - PQC Engine policy upgraded cipher selection (Informational)
- **1 Workbook** — Post-Quantum Cryptography Operations Dashboard with client classification, key exchange groups, policy enforcement, and per-instance metrics
- **1 Playbook** — Teams notification on Sentinel incidents

### Custom Table

- **PQCEngine_CL** — Runtime cryptographic telemetry: handshake negotiations, KEM/signature operations, policy enforcement events, vulnerable algorithm detections, and client classification

### Algorithms Tracked

- ML-KEM-768 (FIPS 203, NIST Level 3)
- ML-KEM-1024 (FIPS 203, NIST Level 5)
- ML-DSA-65 (FIPS 204, NIST Level 3)
- ML-DSA-87 (FIPS 204, NIST Level 5)
- X25519+ML-KEM-768 (hybrid, TLS codepoint 0x11EC)
- secp384r1+ML-KEM-1024 (hybrid, Level 5)
