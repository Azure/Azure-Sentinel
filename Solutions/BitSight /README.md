# BitSight Risk Findings Microsoft Sentinel Solution Package

This package merges the reduced-scope **BitSight Risk Findings CCF connector** with the initial **Microsoft Sentinel solution content**.

## Package structure

### 1. CCF Connector
Located under `CCF Connector/`

Includes:
- `bitsight-risk-findings-connection-template.json`
- `bitsight-risk-findings-connector-definition.json`
- parameter files
- connector README
- connector ReleaseNotes
- `BitsightRiskFindings.kql`

This connector ingests reduced-scope BitSight findings into:

- `BitsightRiskFindings_CL`

Scope:
- Botnet Infections
- Spam Propagation
- Malware Servers
- Unsolicited Communications
- Potentially Exploited
- TLS/SSL Certificates
- Patching Cadence
- Mobile Software
- Open Ports
- File Sharing

Initial ingestion scope:
- **WARN**
- **BAD**

### 2. Content
Located under `Content/`

Includes:
- 1 analytic rule
- 5 hunting queries
- 1 workbook

## Deployment order

1. Publish the connection template from `CCF Connector/` as a Template Spec.
2. Deploy the connector definition from `CCF Connector/`.
3. Open the connector in Microsoft Sentinel and run **Connect** for each BitSight company you want to monitor.
4. Import or package the content from `Content/` into the Sentinel solution.

## Notes

- This merged package keeps the connector and the content together for solution delivery.
- The connector remains a **2-ARM CCF design** because that is how Microsoft Sentinel CCF is structured.
- The content is built for the reduced BitSight findings scope and assumes data is available in `BitsightRiskFindings_CL`.
