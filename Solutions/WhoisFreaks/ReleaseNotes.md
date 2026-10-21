| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|---|---|---|
| 3.0.2 | 21-10-2026 | Fixed the high-confidence threat rule to compare the decimal confidence score (0 to 1) with `todouble(confidence) >= 0.8`; replaced the fixed 5,000-per-hour NRD burst threshold with a seven-day daily baseline comparison. |
| 3.0.1 | 16-10-2026 | Deployment UI now filters workspaces by the exact resource group and lets the workspace region be reviewed before deployment. |
| 3.0.0 | 09-10-2026 | Initial publication with the CCF threat and NRD feeds and four analytic-rule templates. |
