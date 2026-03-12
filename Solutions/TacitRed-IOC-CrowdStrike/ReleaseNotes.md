| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.1       | 17-02-2026                     | Fixed `InvalidResourceLocation` error: removed non-standard `location` parameter from inner template. Added missing `hidden-SentinelTemplateName` and `hidden-SentinelTemplateVersion` tags so playbook template appears in Sentinel Automation. Removed `TacitRed_Domain` filter — playbook now fetches all findings. |
| 3.0.0       | 23-01-2026                     | Initial Solution Release - **Playbook** for automated IOC synchronization between TacitRed and CrowdStrike Falcon. Supports Domain and SHA256 IOC types. |
