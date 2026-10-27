| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
| ---|---|---|
| 3.1.4 | 27-10-2026 | Full playbooks: the Microsoft Sentinel connection now uses the resource group location instead of reference() on the workspace (fixes "The template function 'reference' is not expected at this location" when creating them from the playbook template). |
| 3.1.3 | 27-10-2026 | Full playbooks: renamed the workspace parameter to WorkspaceName (fixes the "Unable to parse language expression" error on Review + create when creating them from the playbook template). Custom connector: the User-Agent header is now fixed and no longer a deployment parameter. |
| 3.1.2 | 24-10-2026 | Clarified the playbook prerequisites: the Silent Push custom connector must be deployed separately (same resource group, name SilentPush-API) before creating any playbook. |
| 3.1.1 | 23-10-2026 | Playbooks now declare a dependency on the SilentPush-API custom connector (fixes the playbook install wizard asking for CustomConnectorName). Added README files with Deploy to Azure buttons for the custom connector and all playbooks. |
| 3.1.0 | 16-09-2026 | Added SilentPush Feeds Data Connector (Codeless/CCP) to ingest Silent Push threat-intel feed exports into SLP_Feeds_CL. |
| 3.0.0 | 20-08-2026 | Initial solution release. |