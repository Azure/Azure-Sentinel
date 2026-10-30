# QCrypton PQC Scanner Agent for Microsoft Sentinel — Release Notes

## v3.0.0 (28-10-2026)

Initial release of the QCrypton PQC Scanner Agent Sentinel Content Hub solution.

### Components

- **1 Data Connector** — Codeless Connector Framework (RestApiPoller) polling QCrypton API for internal network scan findings
- **6 Analytic Rules:**
  - Network appliance serving quantum-vulnerable certificate (High)
  - Internal endpoint using TLS below 1.3 (Medium)
  - New quantum-vulnerable appliance or internal resource appeared (Informational)
  - PQC-ready appliance detected — quantum-safe posture confirmed (Informational)
  - High-risk internal endpoint with critical quantum vulnerability (High)
  - Appliance certificate expiring within 30 days with classical algorithm (Medium)
- **1 Workbook** — Internal Network PQ Readiness dashboard with vendor breakdown, trend analysis, and certificate expiry tracking
- **1 Playbook** — Teams notification on Sentinel incidents

### Supported Appliances

- F5 BIG-IP (LTM, virtual servers, client/server SSL profiles)
- Check Point (certificates, HTTPS inspection rules, gateways)
- Palo Alto PAN-OS (certificates, decryption profiles)
- Cisco ASA/FTD (identity/CA certificates, SSL settings, VPN profiles)
- Fortinet FortiGate (certificates, SSL profiles, firewall policies)

### Azure Endpoints Discovered

- App Services, Function Apps
- Front Door, Application Gateways
- API Management, Container Apps
