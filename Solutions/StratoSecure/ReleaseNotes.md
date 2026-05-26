# StratoSecure Sentinel Solution — Release Notes

## v1.0.0 (2026-06-01)

### New Features

- **Unified ASPM Integration**: Code-level SAST/SCA findings correlated with Microsoft Defender for Cloud runtime evidence
- **5 Custom Sentinel Tables**: StratoSecure_Findings_CL, StratoSecure_ApiInventory_CL, StratoSecure_Remediation_CL, StratoSecure_ScanSummary_CL, StratoSecure_Exception_CL
- **6 Analytics Rules**: S1 (SAST+BruteForce), S2 (Secret+AnomalousCredential), S3 (BOLA+TrafficAnomaly), S6 (CriticalFinding+Overdue), S9 (UnauthenticatedAPI+Internet), S11 (PCI+AuditWindow)
- **8 Watchlists**: CrownJewelApplications, PCIApplications, InternetFacingApps, CriticalApiEndpoints, AcceptedRiskExceptions, ReleaseWindows, RegulatedRepos, HighValueServicePrincipals
- **3 Workbooks**: Executive AppSec Risk, SOC Code Context, API Risk Inventory
- **7 Playbooks**: CreateJiraTicket, CreateADOWorkItem, NotifyTeams, AssignOwner, CreateException, CloseInSentinel, EscalateOwner
- **Compliance Evidence Pack**: PCI-DSS 4.0, CNBV México (Art. 115 Bis 4), SBP Panamá (Acuerdo 011-2018) PDF exports
- **PR Quality Gates**: GitHub Checks API and Azure DevOps Status API blocking merge on Critical/High findings
- **BYO Azure OpenAI**: Route auto-fix LLM calls to tenant-owned endpoints

### Requirements

- Microsoft Sentinel workspace (Log Analytics workspace)
- Azure subscription with Contributor access for DCR and Logic App deployment
- StratoSecure Platform API key (generated at client.stratocode.io)
- GitHub App or Azure DevOps PAT for SCM integration (optional)

### Known Limitations

- CNBV and SBP compliance reports require manual human review before submission to regulators
- Defender for Cloud correlation requires `SecurityAlert.Read.All` Graph permission (admin consent required)
- PR quality gates require GitHub App installation with `checks:write` permission
