# Solution Release Notes

> [!NOTE]
> The legacy SAP agent-based connector reached end of life on 14-09-2026. See the [migration guide](https://learn.microsoft.com/azure/sentinel/sap/sap-agent-migrate) for details.

For the current release notes and version history of the agentless package on SAP Integration Suite, see [Agentless SAP README](./Agentless/README.md).

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
| --- | --- | --- |
| 3.6.0 | 12-11-2026 | Added a preview scheduled **Analytical Rule** in `Analytics/Alerts/Scheduled.json` for potential empty-hour audit log gaps per SAP system/client over 13 days, including intervals older than seven days, plus expected-client watchlist provisioning from Integration Suite onboarding CSV metadata. Source update only; Content Hub packaging and publication are pending. |
| 3.5.11 | 26-10-2026 | Updated "WEBSITE_NODE_DEFAULT_VERSION" from "~12" to "~22" in the Basic-SAPLockUser-STD and SAPCollectorRemediate-STD **Playbooks** deployment configurations. |
| 3.5.10 | 30-06-2026 | Removal of Agent-based connector from solution. Zip file link redirected to SAP Business Accelerator Hub (moved from editable to configure-only release). |

Prior version history (since 2023) for Agent-based connector compacted.
