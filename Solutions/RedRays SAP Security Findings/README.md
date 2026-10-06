# RedRays SAP Security Findings

Bring RedRays SAP security findings into Microsoft Sentinel to review them alongside your
other security data. This preview includes findings from Vulnerability Assessment, ABAP Code
Security, BTP Security, Segregation of Duties, SAP Profile Parameters and Password Security.
Threat Modelling is not included.

RedRays stays in your existing Docker, on-premises or cloud environment and sends findings
through the Azure Monitor Logs Ingestion API on a schedule you choose. The solution supports
Azure public cloud. You need a RedRays license with Microsoft Sentinel integration; Azure
ingestion and retention charges are separate.

This solution covers security assessments. It does not collect SAP Security Audit Log events,
populate `ABAPAuditLog` or activate Microsoft's built-in SAP audit detections.

## Set up the integration

The Content Hub package installs a data connector definition, seven analytics rule templates
and a workbook template. You configure the connection and enable the rules after installation.
The connector guides you through setup; RedRays sends the data. The package does not deploy
a RedRays server, Azure Function, VM or polling agent.

1. **Prepare the workspace and application.** Use a Log Analytics workspace with Sentinel
   enabled. Create a dedicated Microsoft Entra application and credential, or use an approved
   existing service principal. Record the tenant ID, application (client) ID and **service
   principal object ID**. Find the last value under Enterprise applications; it differs from
   the application object ID and client ID.
2. **Deploy the ingestion resources.** Deploy `Deployment/azuredeploy.json` in your workspace's
   resource group and region. You can also download the template from RedRays > Platform
   Settings > Microsoft Sentinel. Leave `deployAnalyticsRules=false` to avoid creating a
   second set of rules. This step creates eight tables, a data collection rule (DCR) for
   direct ingestion and a Monitoring Metrics Publisher role assignment scoped to that DCR.
   Deployment requires resource and role-assignment permissions. RedRays itself needs only
   the ingestion role. Use a dedicated DCR name and a RedRays version with matching table schemas.
3. **Configure RedRays.** Copy `ingestionEndpoint` and `dcrImmutableId` from the deployment
   outputs into RedRays, along with the tenant ID, client ID and secret. Choose the modules
   and export interval, then save and enable the integration. Keep `alertOnBaseline` disabled
   for the first import so you can review the initial findings before creating alerts.
4. **Check delivery.** Send a test event, then wait for a scheduled export. Query
   `RedRaysExportHealth_CL` for `RecordKind == 'HEARTBEAT'`. A successful test means Azure
   accepted the request; the data may take time to appear in queries.
5. **Enable the content you need.** In Manage solution, create the workbook and your chosen
   analytics rules. Review the initial findings first. Set the export health threshold above
   your export interval, allowing time for ingestion.

Allow outbound HTTPS from RedRays to Microsoft Entra and the Azure Monitor ingestion endpoint.
No inbound connection to RedRays is required. Rotate the application credential in Entra and
update it in RedRays before it expires. Keep credentials out of the solution package.

## Tables

| Table | Content |
|---|---|
| RedRaysVulnerabilities_CL | SAP vulnerability assessment findings |
| RedRaysAbapFindings_CL | ABAP source code findings |
| RedRaysCloudFindings_CL | SAP BTP security findings |
| RedRaysSoDFindings_CL | Segregation of duties findings |
| RedRaysProfileChecks_CL | Profile parameter checks |
| RedRaysPasswordFindings_CL | Positive password security detections |
| RedRaysScanRuns_CL | Exported scan metadata and coverage |
| RedRaysExportHealth_CL | Export health and connectivity tests |

## How alerts work

Most finding rules select actionable High or Critical findings with `IsAlertCandidate=true`.
The profile rule selects `SourceStatus=VULNERABLE` and raises Medium severity alerts. These
rules use the same KQL as the RedRays deployment template: they cover new or materially changed
findings, plus baseline findings if you enable baseline alerting. Assessment findings do not
establish that an attack occurred, so the templates do not assign ATT&CK mappings.

Rules run every 15 minutes and look back one day. Older events fall outside that window.
If you change the rule frequency, adjust its ingestion-time filter too and test with delayed
data. `EventId` removes repeated deliveries within the query window, while `FindingKey`
identifies a finding within a RedRays instance and module. Delivery is at least once, so
duplicate incidents remain possible. Records from separate scans may have different identities
and are not automatically merged.

The export health rule alerts after 60 minutes without a heartbeat by default. It needs at
least one heartbeat in its one-day query window: it cannot detect an instance that never
connected or has been silent for longer than a day. Monitor those cases separately. The
connector's Connected badge uses a two-day heartbeat window and does not confirm that every
selected module is exporting.

Finding updates do not close Sentinel incidents automatically. A finding deleted at the
source is not treated as resolved.

## Reading the data

Daily snapshots let you query the latest findings within the retention period. An empty result
alone does not mean a system is clean: check source timestamps, scan coverage and export health.
Profile check severity follows the integration's policy; custom profile parameters are unrated.
Password findings show detected issues, but do not establish that a full password audit completed.
See `Deployment/setup.json` for these details.

The deployment uses Analytics tables with 30-day retention. Azure bills ingestion and retention
to your subscription.

## Upgrades and removal

Export any rules and workbooks you have customized before upgrading. Review template changes
before applying them, and test the upgrade in a separate workspace. Disable equivalent rules
from earlier standalone deployments to avoid duplicate alerts. When redeploying ingestion
resources, reuse this integration's DCR name and sender principal; keep other integrations on
their own DCRs.

To stop exports, disable the integration in RedRays. Uninstalling the Content Hub solution does
not delete ingested data or revoke sender access. Review your rules, workbooks, DCR and its role
assignment separately, and retain the tables according to your organization's policy.

For help, contact [RedRays support](mailto:support@redrays.io) or visit [redrays.io](https://redrays.io/).

## Before publishing

Building the package does not complete release validation. Maintainers should:

- Confirm the assessment scope with Microsoft before making SAP partner add-on compatibility claims.
- Install in a clean Sentinel workspace and check the connector and workbook.
- Test all six modules, initial and changed findings, retries, multiple RedRays instances,
  disabled modules and delayed ingestion.
- Create rules from the templates and check incidents, heartbeat alerts and threshold changes.
- Test redeployment and upgrades, then capture light and dark workbook previews for the registry.
- Check the shared logo and workbook registry entries, and update the publish dates for the release.
- Submit the reviewed sources to Azure-Sentinel and the build package to Partner Center separately.
