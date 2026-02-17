# Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.2       | 18-02-2026                     | Fixed InvalidTemplate error when deploying playbooks on workspaces with hyphenated names (e.g. `Sentinel-Defender-Prod-7`). Removed non-standard `workspace` parameter from Function App inner template and aligned SENTINEL_WORKSPACE_ID to use `variables('workspace-name')`, matching the standard Content Hub pattern used by 530+ Sentinel solutions. |
| 3.0.1       | 11-02-2026                     | Fixed deployment failure: Restored functionCode.zip package removed in prior commit. Removed workspace-scoped roleAssignments from Function App template to resolve InvalidTemplate error during Content Hub deployment. |
| 3.0.0       | 09-12-2025                     | Initial release of TacitRed Defender Threat Intelligence solution with Azure Function and Logic App playbook for syncing TacitRed compromised credentials to Microsoft Defender Threat Intelligence. |
