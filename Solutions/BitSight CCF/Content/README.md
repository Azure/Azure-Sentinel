# BitSight Risk Findings Solution Content

This folder contains the **solution content artifacts** for the reduced-scope BitSight Risk Findings Microsoft Sentinel solution.

## Included content

- **1 analytic rule**
  - `Analytic Rules/NewBadBitSightRiskFinding.yaml`
- **5 hunting queries**
  - `Hunting Queries/LatestWarnBadBitSightFindings.yaml`
  - `Hunting Queries/ActiveBadBitSightFindingsByCompany.yaml`
  - `Hunting Queries/BitSightFindingTrendByRiskVector.yaml`
  - `Hunting Queries/NewlyObservedBadBitSightFindingsLast24Hours.yaml`
  - `Hunting Queries/CompanyRiskPostureSummary.yaml`
- **1 workbook**
  - `Workbooks/BitSightRiskFindingsOverview.json`

## Scope

This content is designed for the reduced BitSight Risk Findings connector and assumes data is ingested into:

- `BitsightRiskFindings_CL`

The content focuses on the agreed reduced monitoring scope:
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

The initial release is scoped to **WARN** and **BAD** findings.

## Notes

- The analytic rule is designed as a **scheduled rule template**.
- The workbook is provided as an ARM template for a shared Azure workbook.
- The hunting queries are provided in Azure Sentinel repository-style YAML format.
