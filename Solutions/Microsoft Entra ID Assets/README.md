# Microsoft Entra ID Assets

This solution contains the legacy data-lake connector, **Microsoft Entra ID Assets**
for Azure Log Analytics (marked Preview by the portal), and one shared schema-normalization
parser. Deprecation applies to the legacy connector, not to the solution.

> **Draft preview:** The new connector references the onboarded Microsoft-managed
> Entra tables. Release readiness and coordinated publication of the replacement
> and deprecation notice require maintainer review. No retirement date or automatic
> cutover is established by this draft.

## Set up the Graph connector

The connection requires read and write permissions on the target workspace and
the Microsoft Entra Global Administrator or Security Administrator tenant role.

1. Install the solution in a Microsoft Sentinel-enabled Log Analytics workspace and
   open **Microsoft Entra ID Assets** with the portal's **Preview** label.
2. In the workspace's deployment tenant, register a single-tenant Microsoft Entra app.
   No redirect URI is required. Copy its Application (client) ID, not its Object ID.
3. Add Microsoft Graph **application** permissions and grant administrator consent:
   `Application.Read.All`, `Device.Read.All`, `Group.Read.All`, `GroupMember.Read.All`,
   `OrgContact.Read.All`, `User.Read.All`, `User-LifeCycleInfo.Read.All`,
   `Organization.Read.All`, `RoleManagement.Read.Directory`,
   `RoleEligibilitySchedule.Read.Directory`, and
   `PrivilegedEligibilitySchedule.Read.AzureADGroup`.
   Add `Member.Read.Hidden` when collecting hidden memberships.
4. Create a client secret and copy its **Value**, not its Secret ID. Store it securely
   and rotate it before expiration. Provide a unique connection name, tenant ID,
   application client ID, and secret through the connector's **Add connection** pane.
5. In **Tables to collect**, select at least one table. All twelve are selected by
   default. Selecting an asset table enables both its snapshot and hourly changefeed
   where supported; selecting a relationship table enables all its collection paths.
6. Check each selected collector's deployment status and table freshness. Collecting
   `EntraEligibleMembers` requires Microsoft Entra ID P2 or Microsoft Entra ID Governance.
   Leave it unselected if that dataset is not needed or the tenant is not licensed.
   A failed eligibility
   collector does not establish that the other collectors failed or succeeded.

The connector supports multiple named connections. With every table selected, it
uses 23 pollers: 17 weekly snapshot paths and six hourly asset changefeeds. Only
pollers for the tables selected during setup are deployed.
The connector page summarizes weekly preview updates; this wording does not disable
the six existing hourly changefeeds.

### Change or stop collection

**Tables to collect is a setup selector, not a live on/off switch.** Unchecking a
previously enabled table does not stop or delete its existing pollers. To stop it,
select and delete all poller rows for that table and connection in the connections
grid, including both snapshot/changefeed rows or every relationship path. Reconnect
with the desired selection as needed. Changing the connection name creates a separate
connection; it does not stop the old one.

Existing table data is retained. In-flight work may still complete after disconnect.

| Dataset | System table | Collection |
| --- | --- | --- |
| Applications | `EntraApplications` | Weekly snapshot; hourly changes |
| Devices | `EntraDevices` | Weekly snapshot; hourly changes |
| Groups | `EntraGroups` | Weekly snapshot; hourly changes |
| Organizational contacts | `EntraOrgContacts` | Weekly snapshot; hourly changes |
| Service principals | `EntraServicePrincipals` | Weekly snapshot; hourly changes |
| Users | `EntraUsers` | Weekly snapshot; hourly changes |
| Organizations | `EntraOrganizations` | Weekly snapshot |
| Transitive group user memberships | `EntraGroupMemberships` | Weekly snapshot |
| Direct members | `EntraMembers` | Weekly snapshot |
| Owners | `EntraOwners` | Weekly snapshot |
| Sponsors | `EntraSponsors` | Weekly snapshot |
| Eligible members | `EntraEligibleMembers` | Weekly snapshot |

Use the table names above in queries and poller data types. The DCR routes raw Graph
custom input streams to standard output streams such as `Microsoft-EntraApplications`.
Custom input stream declarations describe the Graph payload; they are not custom
workspace tables. No custom table creation resources are included.
The new connector's internal ID is `MicrosoftEntraIDAssetsCCF`; the legacy connector's
existing ID remains unchanged.

### Collection limitations

- Hourly changefeeds start with `$deltatoken=latest`, not an initial full enumeration.
  Continuation and delta links are persisted. Snapshots provide the separate baseline;
  consumers must reconcile changes, deletion tombstones, and at-least-once delivery.
- `FeedTypeVersion` is a string containing the Sunday UTC calendar-week bucket for
  snapshot rows; it is empty for changefeed rows. It is not a unique crawl ID or a
  completion watermark. Same-week runs share a bucket and a run crossing the week
  boundary can span two buckets.
- Nested collection is preview. Group parent paging uses Graph's default page size;
  transitive user membership children use `$top=999` and eventual consistency.
  Prior paging checks do not establish complete collection at production scale.
- Direct group-member collection uses Microsoft Graph **beta** to include service
  principals. Beta APIs are not supported for production applications.
- Sponsors, transitive memberships, and eligibility snapshots can take days in large
  tenants. The connector's five-day estimate is not a maximum or SLA. Early rows do
  not establish snapshot completion.
- Complete end-to-end ingestion and live parser execution have not been established by this
  draft. Validate in a nonproduction workspace before planning a production cutover.

## Schema normalization

**Parser for Microsoft Entra ID Assets** installs the single function
`EntraAssetsNormalize(T:(*))`. It accepts a queryable asset or relationship table and
converts legacy camelCase fields to the PascalCase names and types used by the new
connector. It also accepts existing PascalCase input.

```kusto
EntraUsers
| invoke EntraAssetsNormalize()
| project Id, DisplayName, AADTenantId, AccountEnabled
```

The output is a shared 126-column schema; project the dataset-specific fields needed
by your query. Nonapplicable fields remain empty or null. PascalCase columns take
precedence by **column presence**, including explicit nulls, false, zero, and empty
values. Source tenant mapping accepts `AADTenantId`, `aadTenantId`, or `tenantId`,
never the Log Analytics workspace `TenantId`. Device `Id` is not inferred from
`DeviceId`. Extra legacy fields are not retained, and missing feed metadata is not
invented.

This is query-time adaptation, not physical migration, data transport, automatic
query rewriting, or snapshot/changefeed reconstruction. Installing a Log Analytics
function does not establish its availability in the data-lake query engine. To
validate against existing lake system tables, first confirm supported function
syntax and data access in that environment; the query body can be tried as an inline
tabular function. Lake execution remains unverified.

## Migrate from the legacy connector

1. Inventory existing queries and downstream dependencies, especially Purview data
   risk graphs. The new Log Analytics connector is **not established as an equivalent
   backend for those graphs**. Do not disconnect their source without owner confirmation.
2. Configure the replacement in a nonproduction workspace. Review permissions,
   licensing, preview/beta limitations, and Log Analytics ingestion and retention costs.
3. Verify every required dataset, paging, identity and field mappings, baseline
   completeness, delta reconciliation, and freshness. Review affected queries for the
   new table names, PascalCase fields, and changed collection semantics.
4. Where needed, use the normalization parser for accessible legacy data. It does not
   move historical data into Log Analytics or make unchanged legacy queries compatible.
5. Only after validation and dependency approval, explicitly disconnect the legacy
   collector using its existing controls. A Content Hub update or deprecation label
   does not stop existing collection or migrate connections and historical data.

Keep the legacy connector available for existing installations during review. This
draft does not remove its resource identity, instructions, connectivity checks, or
disconnect capability, and does not promise that it is hidden from new users.

## References

- [Microsoft Graph delta query](https://learn.microsoft.com/en-us/graph/delta-query-overview)
- [Direct group members and beta workaround](https://learn.microsoft.com/en-us/graph/api/group-list-members?view=graph-rest-1.0)
- [PIM licensing](https://learn.microsoft.com/en-us/entra/id-governance/licensing-fundamentals)
- [Log Analytics cost management](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/cost-logs)
- [Purview data risk graphs](https://go.microsoft.com/fwlink/?linkid=2320023)
