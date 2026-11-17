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

The Content Hub package installs a Codeless Connector Framework (CCF) push connector, six
analytics rule templates and a workbook template. You deploy the ingestion resources from the
connector page and enable the rules after installation. RedRays sends the data. The package does
not deploy a RedRays server, Azure Function, VM or polling agent.

1. **Deploy the push connector resources.** In Microsoft Sentinel, open **Data connectors >
   RedRays SAP Security Findings** and select **Deploy**. Sentinel creates a data collection
   endpoint (DCE), a data collection rule (DCR) and the eight RedRays tables, then registers a
   Microsoft Entra application with a client secret and grants it the Monitoring Metrics
   Publisher role on the DCR. You need permission to create app registrations and to assign
   roles on the DCR. Copy the client secret immediately; it is shown only once.
2. **Configure RedRays.** In RedRays > Platform Settings > Microsoft Sentinel, enter the tenant
   ID, application (client) ID, client secret, DCE URI and DCR immutable ID shown on the
   connector page. Choose the modules and export interval, then save and enable the integration.
   Keep `alertOnBaseline` disabled for the first import so you can review the initial findings
   before creating alerts.
3. **Check delivery.** Send a test event, then wait for a scheduled export. Query
   `RedRaysExportHealth_CL` for `RecordKind == 'HEARTBEAT'`. A successful test means Azure
   accepted the request; the data may take time to appear in queries.
4. **Enable the content you need.** In Manage solution, create the workbook and your chosen
   analytics rules. Review the initial findings first. Set the workbook export health threshold above
   your export interval, allowing time for ingestion.

Allow outbound HTTPS from RedRays to Microsoft Entra and the data collection endpoint.
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
rules use the same finding-selection logic as the RedRays deployment template: they cover new or materially changed
findings, plus baseline findings if you enable baseline alerting. Assessment findings do not
establish that an attack occurred, and must not be interpreted as observed adversary behavior.
Each rule's ATT&CK mapping describes how an adversary could abuse the reported weakness:

| Rule | Tactics | Techniques |
|---|---|---|
| Vulnerability Assessment | InitialAccess, PrivilegeEscalation | T1190, T1068 |
| ABAP Code Security | InitialAccess, PrivilegeEscalation | T1190, T1068 |
| Cloud Security | InitialAccess, PrivilegeEscalation | T1078 |
| SoD | PrivilegeEscalation, Persistence | T1078 |
| Profile Parameters | DefenseEvasion, CredentialAccess | T1562, T1110 |
| Password Security | CredentialAccess | T1110 |

The password mapping covers authorized password recovery without asserting an online or
offline sub-technique.

Finding rules provide Host, IP and URL entity mappings. If source links are relative, configure
`redRaysPortalUrls` in each rule query, for example `dynamic({"<ProductInstanceId>": "https://redrays.example"})`.
Use a separate origin for each RedRays installation. Missing or invalid links do not create URL
entities. SAP user names remain in custom details with the product instance, system and client;
they are not treated as global account identities. Cloud findings may have no host, so configure
the portal origin to enable their URL investigation link.

Rules run every 15 minutes and look back one day. Older events fall outside that window.
If you change the rule frequency, adjust its ingestion-time filter too and test with delayed
data. `EventId` removes repeated deliveries within the query window, while `FindingKey`
identifies a finding within a RedRays instance and module. Delivery is at least once, so
duplicate incidents remain possible. Records from separate scans may have different identities
and are not automatically merged.

The workbook flags a previously connected instance as STALE after 60 minutes without a
heartbeat. Set the threshold above the export interval and expected ingestion delay.
Only instances with a heartbeat in the selected time range are visible; never-connected
instances require a separate expected-instance inventory. Heartbeat loss is operational
monitoring and has no ATT&CK mapping, so it is not packaged as a Sentinel analytics rule.
For notifications, configure an Azure Monitor log search alert separately. The connector's
Connected status shows that the push connector is deployed; it does not confirm every module is exporting.

Finding updates do not close Sentinel incidents automatically. A finding deleted at the
source is not treated as resolved.

## Reading the data

The workbook time-range selector applies to findings, export health and scan coverage.
Daily snapshots let you query the latest findings within the retention period. An empty result
alone does not mean a system is clean: check source timestamps, scan coverage and export health.
Profile check severity follows the integration's policy; custom profile parameters are unrated.
Password findings show detected issues, but do not establish that a full password audit completed.

The connector creates Analytics tables that use the workspace's default retention. Azure bills
ingestion and retention to your subscription.

## Upgrades and removal

Export any rules and workbooks you have customized before upgrading. Review template changes
before applying them, and test the upgrade in a separate workspace. Disable equivalent rules
from earlier standalone deployments to avoid duplicate alerts. If you previously deployed the
standalone RedRays ARM template, switch RedRays to the connector's DCE URI, DCR immutable ID and
application credentials, then remove the old DCR and its role assignment.

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
- Create rules from the templates and check incidents and workbook heartbeat threshold changes.
- Test redeployment and upgrades, then capture light and dark workbook previews for the registry.
- Check the shared logo and workbook registry entries, and update the publish dates for the release.
- Submit the reviewed sources to Azure-Sentinel and the build package to Partner Center separately.

## Connector architecture and packaged assets

RedRays scheduler -> Microsoft Entra token endpoint -> data collection endpoint (Logs Ingestion API) -> DCR -> Log Analytics.
The connector is a CCF `Push` connector defined in `Data Connectors/RedRaysSAPSecurityFindings_PUSH_CCP/`:
the connector definition, the push data connector, one DCR with a stream per table, and the eight table schemas.
The sender runs in the customer-controlled RedRays backend; there is no Azure Function or polling component.
The connector references the raw SVG URL under the repository's `Logos/` folder for portal rendering; a copy is also included as
`Data Connectors/RedRays.svg`. Light and dark previews are included inside
`Workbooks/Images/Preview/` as well as the repository workbook gallery.
