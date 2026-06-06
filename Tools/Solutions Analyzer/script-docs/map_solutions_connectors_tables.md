# Solution Connector Tables Analyzer

**Script:** `map_solutions_connectors_tables.py`

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Running the Script](#running-the-script)
- [Command Line Options](#command-line-options)
- [Override System](#override-system)
  - [Synthetic Connector Overrides](#synthetic-connector-overrides)
- [Output Files](#output-files) — see also [`csv/`](csv/README.md) for per-CSV reference
- [Azure Marketplace Availability](#azure-marketplace-availability)
- [Detection Logic](#detection-logic)
  - [Connector Discovery](#connector-discovery)
  - [Collection Method Detection](#collection-method-detection)
  - [Ingestion API Detection](#ingestion-api-detection)
  - [Custom Log V1 (CLv1) Detection](#custom-log-v1-clv1-detection)
  - [Filter Fields Detection](#filter-fields-detection)
  - [Connector Association Algorithm](#connector-association-algorithm)
  - [Parser Resolution](#parser-resolution)
  - [Table Detection Methods](#table-detection-methods)
  - [Context-Aware Table Detection](#context-aware-table-detection)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The Solution Connector Tables Analyzer is a comprehensive tool that scans the Azure-Sentinel repository to extract, analyze, and document the relationships between Microsoft Sentinel solutions, data connectors, Log Analytics tables, content items, and parsers.

### Key Capabilities

**Data Connector Analysis**
- Extract table references from connector JSON files (queries, sample queries, data types)
- Detect collection methods (AMA, MMA, Azure Diagnostics, CCF, CCF Push, CCF Legacy, Azure Functions, REST API, Native)
- Extract filter fields (DeviceVendor, EventID, Facility, etc.) to identify data sources
- Resolve parser function references to actual underlying tables
- Check Azure Marketplace availability for each solution

**Content Item Analysis**
- Analyze analytics rules, hunting queries, playbooks, workbooks, watchlists, and summary rules
- Extract table references and filter fields from KQL queries
- Classify content by source: Solution, Standalone (community), or GitHub Only (legacy)
- Associate standalone content with matching connectors based on tables and filters

**Parser Analysis**
- Collect parsers from solution directories and legacy `/Parsers/*` directories
- Analyze ASIM parsers with full schema metadata
- Associate parsers with connectors based on shared tables and filter fields
- Support for union parsers and sub-parser resolution

**Solution Metadata**
- Flatten solution metadata from SolutionMetadata.json files
- Include ALL solutions, even those without data connectors
- Track solution support tiers, authors, and categories

### Output

The script generates 11 CSV files providing different views of the data:
- **Entity files**: `connectors.csv`, `solutions.csv`, `tables.csv`, `parsers.csv`, `asim_parsers.csv`
- **Mapping files**: `content_items.csv`, `content_tables_mapping.csv`, `solution_dependencies.csv`, `table_schemas.csv`, `solutions_connectors_tables_mapping_simplified.csv`
- **Reports**: `solutions_connectors_tables_issues_and_exceptions_report.csv`
- **Backward compatibility**: `solutions_connectors_tables_mapping.csv`

### Scope

This analysis covers connectors managed through Solutions in the Azure-Sentinel GitHub repository. For solutions where connectors are defined only as ARM resources in `Package/mainTemplate.json` (not as standalone JSON files in the `Data Connectors` folder), the analyzer uses a mainTemplate fallback mechanism to discover them. Connectors that have no discoverable definition files at all (such as SAP, which uses a Docker agent architecture) can be added via the [synthetic connector override system](#synthetic-connector-overrides).

## Prerequisites

### 1. Clone the Azure-Sentinel Repository

This script analyzes the Solutions directory from the [Azure-Sentinel GitHub repository](https://github.com/Azure/Azure-Sentinel). You must have the repository cloned locally:

```bash
# Clone the repository
git clone https://github.com/Azure/Azure-Sentinel.git

# Or if you already have it, update to latest
cd Azure-Sentinel
git pull origin master
```

The script expects to find the `Solutions/` directory containing Microsoft Sentinel solution definitions.

### 2. Python Environment

- Python 3.7 or higher
- No external dependencies required (optional: json5 for enhanced JSON parsing)

### 3. Table Reference Data (Recommended)

For enriched table metadata (categories, descriptions, transformation support), first run `collect_table_info.py` to generate `tables_reference.csv`:

```bash
python collect_table_info.py
```

The mapping script automatically loads `tables_reference.csv` if present and uses it to:
- Populate table metadata (category, description, resource_types)
- Determine collection method based on table properties (e.g., "Azure Resources" category → Azure Diagnostics)
- Include transformation support and ingestion API compatibility information

See [collect_table_info.md](collect_table_info.md) for details.

### 4. ASIM Schema Field Data (Recommended)

For ASIM schema field information used by the ASIM browser, run `collect_asim_fields.py` to generate `asim_fields.csv`:

```bash
python collect_asim_fields.py
```

The mapping script automatically re-runs `collect_asim_fields.py` when `--force-refresh=asim` or `--force-refresh=all` is used.

See [collect_asim_fields.md](collect_asim_fields.md) for details.

### 5. Optional Dependencies

```bash
pip install json5  # For improved JSON parsing with comments and trailing commas
```

## Running the Script

From the `Tools/Solutions Analyzer` directory:
```bash
python map_solutions_connectors_tables.py
```

Or from anywhere in the repository:
```bash
python "Tools/Solutions Analyzer/map_solutions_connectors_tables.py" --solutions-dir Solutions
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--solutions-dir` | `../../Solutions` | Path to the Solutions directory |
| `--output` | `solutions_connectors_tables_mapping.csv` | Path for the main output CSV file |
| `--report` | `solutions_connectors_tables_issues_and_exceptions_report.csv` | Path for the issues report CSV file |
| `--connectors-csv` | `connectors.csv` | Path for the connectors output CSV file (with collection method) |
| `--solutions-csv` | `solutions.csv` | Path for the solutions output CSV file |
| `--tables-csv` | `tables.csv` | Path for the tables output CSV file (with metadata) |
| `--content-items-csv` | `content_items.csv` | Path for the content items output CSV file |
| `--content-tables-mapping-csv` | `content_tables_mapping.csv` | Path for the content-to-tables mapping CSV file |
| `--asim-parsers-csv` | `asim_parsers.csv` | Path for the ASIM parsers CSV file |
| `--parsers-csv` | `parsers.csv` | Path for the non-ASIM parsers CSV file |
| `--solution-dependencies-csv` | `solution_dependencies.csv` | Path for the solution dependencies CSV file |
| `--table-schemas-csv` | `table_schemas.csv` | Path for the table schemas CSV file extracted from DCR definitions |
| `--la-table-schemas-csv` | `la_table_schemas.csv` | Path to la_table_schemas.csv containing column schemas from Azure Monitor documentation (generated by `collect_table_info.py`) |
| `--custom-tables-dir` | `.script/tests/KqlvalidationsTests/CustomTables` | Path to CustomTables directory for KQL validation table schemas (only `_CL` tables not already covered by DCR or docs are included; non-CL tables are skipped since they should be in the Azure Monitor table reference) |
| `--tables-reference-csv` | `tables_reference.csv` | Path to tables_reference.csv for table metadata |
| `--mapping-csv` | `solutions_connectors_tables_mapping_simplified.csv` | Path for the simplified mapping CSV file |
| `--overrides-csv` | `solution_analyzer_overrides.csv` | Path to overrides CSV file for field value overrides |
| `--show-detection-methods` | `False` | Include table_detection_methods column showing how each table was detected |
| `--skip-marketplace` | `False` | Skip Azure Marketplace availability checking |
| `--refresh-marketplace` | `False` | Force refresh of marketplace cache (ignore cached results) |
| `--force-refresh` | `""` | Force re-analysis of specified types, ignoring cached results. Comma-separated list of: `asim`, `parsers`, `solutions`, `standalone`, `marketplace`, `tables`, `learn_docs`. Use `all` to refresh everything, or `all-offline` to refresh all except network-dependent types. When `tables` is included, also re-runs `collect_table_info.py` with `--refresh-cache`. When `asim` is included, also re-runs `collect_asim_fields.py` with `--refresh-cache`. When `learn_docs` is included, refetches the Microsoft Learn `data-connectors-reference` anchor index. |

### Example Usage

```bash
# Run with default settings
python map_solutions_connectors_tables.py

# Show detection methods in output
python map_solutions_connectors_tables.py --show-detection-methods

# Custom output location
python map_solutions_connectors_tables.py --output custom_output.csv --report custom_report.csv

# Run with custom overrides file
python map_solutions_connectors_tables.py --overrides-csv my_overrides.csv

# Force refresh ASIM and parser analysis
python map_solutions_connectors_tables.py --force-refresh=asim,parsers

# Force refresh table metadata from Microsoft docs
python map_solutions_connectors_tables.py --force-refresh=tables
```

## Override System

The script supports an override system that allows you to modify field values in the output based on pattern matching. This is useful for:
- Setting `collection_method` to AMA for specific tables (e.g., Syslog, CommonSecurityLog)
- Assigning categories to tables based on naming patterns (e.g., all AWS* tables → AWS category)
- Correcting or supplementing data that cannot be automatically detected

The default override file (`solution_analyzer_overrides.csv`) is also used by `collect_table_info.py` and `generate_connector_docs.py` for consistent categorization across all outputs.

### Override File Format

The override file is a CSV with the following columns:

| Column | Description |
|--------|-------------|
| `Entity` | Entity type to match: `table`, `connector`, `solution`, or `synthetic_connector` (case insensitive). See [Synthetic Connector Overrides](#synthetic-connector-overrides) for the special `synthetic_connector` entity type. |
| `Pattern` | Regex pattern to match against the entity's key field (table_name, connector_id, or solution_name) |
| `Field` | The field name to override |
| `Value` | The new value to set |

**Pattern Matching Rules:**
- Patterns are treated as full-match regex (automatically wrapped with `^` and `$`)
- Pattern matching is case insensitive
- Use `.*` for wildcards (e.g., `.*AWS.*` matches any table containing "AWS")
- Field names must exactly match existing columns in the output

### Example Override File

```csv
Entity,Pattern,Field,Value
Table,Syslog,collection_method,AMA
Table,CommonSecurityLog,collection_method,AMA
Table,SecurityEvent,collection_method,AMA
Table,Event,collection_method,AMA
Table,WindowsFirewall,collection_method,AMA
Table,.*AWS.*,category,AWS
Table,.*GCP.*,category,GCP
Table,.*Crowdstrike.*,category,Crowdstrike
Table,.*CRWD.*,category,Crowdstrike
```

This example:
- Sets `collection_method` to "AMA" for common Windows/Syslog tables
- Sets `category` to "AWS" for all tables with "AWS" in their name
- Sets `category` to "GCP" for all tables with "GCP" in their name
- Sets `category` to "Crowdstrike" for tables matching Crowdstrike patterns

### Default Override File

If no `--overrides-csv` argument is provided, the script looks for `solution_analyzer_overrides.csv` in the Tools/Solutions Analyzer directory.

### Synthetic Connector Overrides

In addition to field overrides, the override file supports defining **synthetic connectors** — connectors that have no discoverable definition files in the repository. This is used for connectors that use non-standard architectures (e.g., SAP uses a Docker agent rather than JSON definition files).

#### Format

Synthetic connectors use `Entity = synthetic_connector` and are defined as multiple rows sharing the same `Pattern` (solution folder name) and grouped by `Field = connector_id`:

| Column | Usage for Synthetic Connectors |
|--------|-------------------------------|
| `Entity` | Must be `synthetic_connector` |
| `Pattern` | Solution folder name (e.g., `SAP`) |
| `Field` | One of: `connector_id` (required, starts a new connector group), `title`, `publisher`, `description`, `tables`, `instruction_steps`, `permissions` |
| `Value` | Field value. For `tables`, use semicolon-separated table names (e.g., `Table1_CL;Table2_CL`) |

#### Required Fields

- `connector_id` — unique identifier for the connector (also starts a new connector group)
- `title` — display title
- `publisher` — publisher name

#### Optional Fields

- `description` — connector description text
- `tables` — semicolon-separated list of table names
- `instruction_steps` — JSON-encoded setup instructions
- `permissions` — JSON-encoded permission requirements

#### Example

```csv
Entity,Pattern,Field,Value
synthetic_connector,SAP,connector_id,MicrosoftSentinelSAP,"SAP connector uses Docker agent architecture..."
synthetic_connector,SAP,title,Microsoft Sentinel for SAP,
synthetic_connector,SAP,publisher,Microsoft,
synthetic_connector,SAP,description,"The Microsoft Sentinel solution for SAP allows you to monitor SAP systems...",
synthetic_connector,SAP,tables,ABAPAuditLog_CL;ABAPChangeDocsLog_CL,
```

Synthetic connectors:
- Are only injected if no connector with the same ID was already discovered for the solution
- Appear in output with `connector_files` set to `synthetic_connector_override` and detection method `synthetic_connector_override`
- Trigger a `missing_solution_metadata` issue if the solution lacks a SolutionMetadata.json file

## Output Files

The script generates the following CSVs. See [`csv/`](csv/README.md) for full per-file documentation (columns, use cases, related files).

### Entity tables

| File | Granularity | Doc |
|------|-------------|-----|
| `connectors.csv` | One row per connector | [`csv/connectors.md`](csv/connectors.md) |
| `solutions.csv` | One row per solution (full Marketplace metadata) | [`csv/solutions.md`](csv/solutions.md) |
| `tables.csv` | One row per table referenced by any connector | [`csv/tables.md`](csv/tables.md) |
| `parsers.csv` | One row per non-ASIM parser | [`csv/parsers.md`](csv/parsers.md) |
| `asim_parsers.csv` | One row per ASIM parser | [`csv/asim_parsers.md`](csv/asim_parsers.md) |
| `content_items.csv` | One row per content item | [`csv/content_items.md`](csv/content_items.md) |

### Mapping / edge tables

| File | Granularity | Doc |
|------|-------------|-----|
| `solutions_connectors_tables_mapping_simplified.csv` | (solution × connector × table) | [`csv/solutions_connectors_tables_mapping_simplified.md`](csv/solutions_connectors_tables_mapping_simplified.md) |
| `content_tables_mapping.csv` | (solution × content × table) with `read`/`write` flag for playbooks | [`csv/content_tables_mapping.md`](csv/content_tables_mapping.md) |
| `solution_dependencies.csv` | (solution × dependency) — explicit + ASIM-derived | [`csv/solution_dependencies.md`](csv/solution_dependencies.md) |
| `table_schemas.csv` | (table × column) — DCR + docs + ARM + KQL validation | [`csv/table_schemas.md`](csv/table_schemas.md) |

### Reports

| File | Doc |
|------|-----|
| `solutions_connectors_tables_issues_and_exceptions_report.csv` | [`csv/solutions_connectors_tables_issues_and_exceptions_report.md`](csv/solutions_connectors_tables_issues_and_exceptions_report.md) |
| `asim_parsers_unmatched_report.csv` | [`csv/asim_parsers_unmatched_report.md`](csv/asim_parsers_unmatched_report.md) |

### Backward-compatibility / legacy

| File | Doc |
|------|-----|
| `solutions_connectors_tables_mapping.csv` | [`csv/solutions_connectors_tables_mapping.md`](csv/solutions_connectors_tables_mapping.md) |

## Azure Marketplace Availability

The script queries the Azure Marketplace Catalog API to collect comprehensive metadata for each solution, including availability status, display names, descriptions, popularity, ratings, categories, and publication dates.

### How It Works

1. For each solution, the script constructs a legacy product ID from the `publisher_id` and `offer_id` in `SolutionMetadata.json`
2. It queries the Azure Marketplace Catalog API at `https://catalogapi.azure.com/offers/{legacy_id}?api-version=2018-08-01-beta`
3. If the API returns a valid response, the full response is parsed into 19 `mp_*` fields and cached
4. If the API returns an error or no data, the solution is marked as unpublished with empty metadata fields

### Collected Fields

The full response is parsed into 19 `mp_*` fields plus the legacy `is_published` and `marketplace_url` fields. See [`csv/solutions.md` › Marketplace metadata](csv/solutions.md#marketplace-metadata-mp_--from-azure-marketplace-catalog-api) for the complete column list.

### Caching

To avoid excessive API calls on subsequent runs, marketplace data is cached locally:

- **Cache Location:** `.cache/marketplace_data.json`
- **Cache Format:** JSON dictionary keyed by `legacy_id`, each value containing all `mp_*` fields
- **Cache Behavior:** 
  - If a solution's legacy ID is found in the cache, the cached result is used (no API call)
  - New solutions not in the cache trigger API calls and are added to the cache
  - Use `--refresh-marketplace` or `--force-refresh marketplace` to force refresh all entries
- **Migration:** The script automatically migrates from the old CSV cache format (`marketplace_availability.csv`) to the new JSON format on first run

### Command Line Options

| Option | Description |
|--------|-------------|
| `--skip-marketplace` | Skip marketplace checking entirely (outputs will have empty marketplace fields) |
| `--refresh-marketplace` | Force refresh of marketplace cache, ignoring cached results and re-querying all solutions |
| `--force-refresh marketplace` | Same as `--refresh-marketplace` (via the unified `--force-refresh` mechanism) |

### Output Fields

Marketplace data adds 19 `mp_*` fields plus the legacy `is_published` and `marketplace_url` fields to [`solutions.csv`](csv/solutions.md). The `is_published` flag is also propagated to [`connectors.csv`](csv/connectors.md), [`content_items.csv`](csv/content_items.md), and the main mapping CSV. For connectors, the propagated solution-level value is overridden to `false` when the connector is absent from a working solution definition file — see [Flagging Connectors Not in the Solution Definition as Unpublished](#flagging-connectors-not-in-the-solution-definition-as-unpublished).

> Solutions without valid `publisher_id` and `offer_id` in `SolutionMetadata.json` cannot be checked and will have empty marketplace fields.

## Detection Logic

### Connector Discovery

The analyzer uses a multi-tier approach to discover connectors within each solution:

#### Primary: Data Connectors Folder Scan

The primary discovery method scans JSON files in the solution's `Data Connectors/` folder (or paths listed in the Solution JSON). Each JSON file is searched using a depth-first traversal (`find_connector_objects`) for dictionaries containing the required connector fields (`id`, `publisher`, `title`). When a connector's `id` field contains an ARM template variable reference (e.g., `[variables('_uiConfigId10')]`), the ID is generated from the title by removing spaces and hyphens (e.g., `Microsoft Power Automate` → `MicrosoftPowerAutomate`).

#### Fallback: mainTemplate.json

If the primary scan finds no connectors for a solution (or finds connectors with ARM variable IDs only), the analyzer falls back to scanning `Package/mainTemplate.json`. This handles solutions where connectors are defined only as ARM resources of type `Microsoft.SecurityInsights/dataConnectorDefinitions` rather than as standalone JSON files. The function:

1. Searches for ARM resources with type ending in `dataConnectorDefinitions`
2. Extracts the `connectorUiConfig` from the resource properties
3. Resolves ARM variable references in the `id` and `publisher` fields using title-based generation
4. Extracts tables from the `dataTypes` section (filtering out `{{...}}` template placeholders)
5. Deduplicates against connectors already found by the primary scan using both ID and title matching

This mechanism discovered the Microsoft Dataverse, Microsoft Power Automate, and Microsoft Power Platform Admin Activity connectors from the Microsoft Business Applications solution.

#### Override: Synthetic Connectors

Connectors that have no discoverable definition files at all can be injected via the [synthetic connector override system](#synthetic-connector-overrides). These are only added if no connector with the same ID was already discovered. See [Synthetic Connector Overrides](#synthetic-connector-overrides) for details.

#### Solution Membership

Both mainTemplate and synthetic connectors are classified as **"In Solutions"** (i.e., `not_in_solution_json = false`), not as "Discovered". mainTemplate connectors are ARM resources defined within the solution's package template, and synthetic connectors are explicitly declared as part of a solution via the override CSV. This matches their status as formally documented solution components on Microsoft Learn.

#### Skipping Solution-Package ARM Templates

Some solutions commit a full **solution-package deployment template** inside their `Data Connectors/` folder (typically named `azuredeploy_*.json`). These files bundle the entire packaged solution — analytic rules, hunting queries, playbooks, workbooks, and parsers as `contentTemplates`, plus a single `contentPackages` resource — and also embed the solution's data connector(s) as ARM resources.

The analyzer detects and **skips** these package templates during connector discovery (`is_solution_package_template`). Detection is name-agnostic and keys solely on the presence of a resource whose `type` ends with `contentPackages`, which never appears in a genuine standalone connector ARM template. Skipping is necessary because:

- The connectors embedded in a package template are already discovered from their authoritative `*_DataConnectorDefinition.json` / `Connector_*.json` definition files.
- The embedded ARM resources often carry a different (legacy) `title` than the standalone definition, so the title-based azuredeploy deduplication does not catch them. Mining the package template would therefore create a **phantom connector** with the wrong title and a merged/incorrect table list.

> Intra-file azuredeploy deduplication: the title-based dedup also applies **within a single** `azuredeploy_*.json` file. Some wrappers emit two connector resources for the same logical connector — one whose `id` resolves to a literal value (`id_generated = false`) and one whose `id` is an unresolvable ARM expression and therefore gets a synthetic title-derived id (`id_generated = true`). When a generated-id entry shares its `title` with a literal-id entry from the same file, the generated entry is skipped (reason `azuredeploy_duplicate_skipped`). Example: Cisco Meraki's `azuredeploy_Cisco_Meraki_native_poller_connector.json` emits both the literal `CiscoMerakiNativePoller` and a title-generated `CiscoMeraki(usingRESTAPI)` — both titled "Cisco Meraki (using REST API)"; only the literal `CiscoMerakiNativePoller` is kept.

Each skipped file is recorded in the issues report with reason `solution_package_template_skipped`. Note this is distinct from a genuine standalone `azuredeploy_*.json` that contains only a single `dataConnectors` resource (no `contentPackages`): those are legacy connector definitions and are still discovered normally (flagged `not_in_solution_json = true` when not listed in the Solution JSON).

#### Flagging Connectors Not in the Solution Definition as Unpublished

The solution definition file (`Solution_*.json`) is the authoritative list of which connectors ship to the content hub. After all rows are built, the analyzer applies a definition-authoritative publishing rule per solution:

- If **at least one** of a solution's connectors is referenced by its definition file (i.e. some connector resolved to `not_in_solution_json = false`), the definition mechanism is proven to work for that solution. Any **additional** connectors found only by scanning the solution's `Data Connectors/` folder — those flagged `not_in_solution_json = true` — are **retained** but marked **`is_published = false`** for that solution association: they were discovered, they are simply not on the content hub. They are no longer dropped. The canonical `connectors.csv` record is forced to `is_published = false` only when the connector is folder-only in **every** solution it appears in; a connector documented by at least one solution stays published through that solution.
- If **no** connector matches the definition (the solution has no definition file, or it references none of the discovered connectors), the folder scan is the only available discovery source, so a definition miss cannot be reliably distinguished from genuine absence. Those folder-discovered connectors are retained at their **solution-level marketplace** `is_published` status (not forced to `false`). This preserves behaviour for definition-less solutions and for solutions whose connectors are only ever discovered from the folder.

> Definition-file discovery: the definition is normally `Data/Solution_*.json`. A few solutions use a non-standard name (e.g. `Solutions_AzureDataLake.json` (plural), `CTM360.json` (no prefix), `OpenSystems_Solution_Input.json`). When no `Solution_*.json` matches, the analyzer falls back to scanning the `Data/` folder for a **definition-shaped** JSON — one with a top-level `Name` plus at least one content array (`Data Connectors`, `Analytic Rules`, `Workbooks`, ...) — excluding generated side-cars (`system_generated_metadata.json`, `SolutionMetadata.json`). The fallback is adopted only when **exactly one** candidate is found, so a metadata look-alike can never be mistaken for the authoritative definition. This ensures the connectors of these solutions are correctly recognised as documented (`not_in_solution_json = false`) instead of appearing as folder-only "discovered" connectors.

> Canonical attribution across multiple source files: a connector id can legitimately appear in several mapping rows sourced from different files — e.g. `1Password` is mapped from both the definition-referenced `1Password_API_FunctionApp.json` (documented) and a non-referenced `deployment/1Password_data_connector.json` wrapper. The per-connector `connectors.csv` record takes its `not_in_solution_json` from the first row processed for that id; to avoid a documented connector being labelled "discovered" just because an undocumented row sorted first, the canonical flag is re-asserted to `false` whenever the connector id is documented in **any** `(solution, connector)` association.

This keeps the full discovered-connector inventory (nothing is deleted) while removing orphaned or superseded leftover artifacts — for example the Okta `OktaSSO_Polling` legacy `APIPolling` template under `OktaNativePollerConnector/`, when the Okta solution definition references only `OktaSSO` and `OktaSSOv2` — from the **published** count. Each folder-only `(solution, connector)` association is recorded in the issues report with reason `connector_not_in_solution_definition`.

> File-name matching note: the documented-vs-folder-only check compares each connector's `Data Connectors/` file name against the file names listed in the definition. The status map is keyed by the **raw on-disk** file name, so the lookup decodes (`unquote`) the URL-encoded file name taken from the generated GitHub URL before comparing. Without this decode, any connector whose file name contains a space or parenthesis — e.g. `CEF AMA.json` (`CefAma`), `Windows Firewall.json` (`WindowsFirewall`), `template_ExtraHopReveal(x)AMA.json` — would fail the match and be wrongly marked `is_published = false` even though it **is** referenced by the definition.


> Note: `mainTemplate` and synthetic connectors are classified `not_in_solution_json = false`, so they are never flagged by this rule. Standalone (non-solution) connectors carry an empty `not_in_solution_json` value and go through a separate code path; they are likewise unaffected.

### Collection Method Detection

The analyzer determines the data collection method used by each connector through comprehensive content analysis. This analysis sets the `collection_method` and `collection_method_reason` columns in `connectors.csv`.

#### Collection Methods

| Method | Description | Detection Criteria |
|--------|-------------|-------------------|
| **Azure Monitor Agent (AMA)** | Modern log collection agent | Title contains "AMA" or "via AMA", ID ends with "ama", `sent_by_ama` field, "Azure Monitor Agent" in description, "CEF via AMA" or "Syslog via AMA" patterns |
| **Log Analytics Agent (MMA)** | Legacy Microsoft Monitoring Agent (deprecated) | Title mentions "Legacy Agent", "omsagent" references, "cef_installer.py" scripts, workspace ID/key patterns, `OmsSolutions` patterns, `InstallAgentOnVirtualMachine`/`InstallAgentOnNonAzure`/`InstallAgentOnLinuxNonAzure` patterns. Special case: connector ID `WindowsFirewall` (without Ama suffix) |
| **Azure Diagnostics** | Azure resource diagnostic settings | "AzureDiagnostics" references in content, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings` resource, Azure Policy diagnostics (`policyDefinitionGuid` + `PolicyAssignment`), table category "Azure Resources" |
| **Native** | Built-in Sentinel integrations | `SentinelKinds` property present, Microsoft Defender/365/Entra ID connectors, known native connector IDs (`AzureActivity`, `AzureActiveDirectory`, `Office365`, `MicrosoftDefender`) - skipped if CCF content patterns detected |
| **Codeless Connector Framework (CCF)** | Microsoft's codeless connector platform (CCP/CCF) | `pollingConfig` present, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (except AMA title connectors), ID contains "CCP"/"CCF"/"Codeless", ID contains "Polling" |
| **CCF Push** | CCF Push mode (partner pushes data via DCR/DCE) | `DeployPushConnectorButton` in connector definition (DCR/DCE-based push ingestion) |
| **CCF (Legacy)** | Legacy CCF with embedded pollingConfig | Initially detected as CCF, but reclassified when `pollingConfig` is found in the primary connector JSON and no separate CCF config file exists |
| **Azure Function** | Azure Functions-based data collection | Filename contains "FunctionApp"/"function_app"/"_api_function", description mentions "Azure Functions", ID contains "AzureFunction"/"FunctionApp", "Deploy to Azure" + "Function App" patterns, "Azure Function App" in content, Azure Functions pricing references |
| **REST API** | Direct API push/webhook collection | "REST API" in title/description, "push" in title/ID, webhook patterns, HTTP endpoint/trigger references |
| **Unknown (Custom Log)** | Method could not be determined | Only custom log table (`_CL`) references found, no other patterns matched |

#### Detection Priority

The detection algorithm uses a tiered priority system with 11 levels. When a connector explicitly declares its type in the title (e.g., "via AMA"), that takes precedence. Otherwise, patterns are detected in the following order:

| Priority | Detection Category | Detection Patterns |
|----------|-------------------|-------------------|
| **1** | **Explicit AMA/MMA in title** (highest) | Title contains "AMA", "via AMA", ID ends with "ama", title contains "Legacy Agent" or "via Legacy Agent". Special: `WindowsFirewall` connector is MMA. |
| **2** | **Azure Function filename** | Filename contains "FunctionApp"/"function_app"/"_api_function", ID contains "AzureFunction"/"FunctionApp" |
| **3** | **CCF content patterns** | `pollingConfig`, `dcrConfig` with `RestApiPoller`, `GCPAuthConfig`, `dataConnectorDefinitions` (unless AMA title). **CCF Push**: `DeployPushConnectorButton` (separately classified as "CCF Push") |
| **4** | **Azure Diagnostics** | "AzureDiagnostics" in content, "diagnostic settings" in description, `Microsoft.Insights/diagnosticSettings`, Azure Policy diagnostics. Skipped if Azure Function filename detected. |
| **5** | **CCF name patterns** | ID contains "CCP"/"CCF"/"Codeless", ID contains "Polling". Skipped if Azure Diagnostics patterns found. |
| **6** | **Azure Function content** | "Azure Functions" in description, "Deploy to Azure" + "Function App", Azure Functions pricing. Skipped if CCF content detected. |
| **7** | **Native Microsoft** | `SentinelKinds`, Microsoft Defender/365/Entra ID titles, known native IDs. Skipped if CCF content detected. |
| **8** | **Secondary AMA/MMA** | `sent_by_ama`, "omsagent", "CEF/Syslog via AMA", "cef_installer.py", workspace ID/key, `OmsSolutions`, `InstallAgent*` patterns |
| **9** | **REST API** | "REST API" in title/description, "push"/"webhook"/"http endpoint" patterns |
| **10** | **Table metadata fallback** | Table category "Azure Resources" → Azure Diagnostics, "virtualmachines" in resource_types → AMA. Only if no stronger patterns. |
| **11** | **Custom log fallback** (lowest) | `_CL` table suffix, no other patterns matched |

#### Final Selection Logic

After all patterns are detected, the final method is selected using this priority order:
1. If title explicitly indicates AMA → select AMA
2. If title explicitly indicates MMA → select MMA
3. Otherwise: Azure Diagnostics > CCF Push > CCF > Azure Function > Native > MMA > AMA > REST API > Unknown
4. Post-processing: CCF connectors with `pollingConfig` in primary JSON and no separate config file are reclassified as **CCF (Legacy)**

#### CSV Fields Affected

| Field | Description |
|-------|-------------|
| `collection_method` | The detected collection method (in `connectors.csv`) |
| `collection_method_reason` | Explanation of why this method was selected |
| `dcr_definition_files` | Semicolon-separated GitHub URLs to companion DCR files associated with the connector (for example `*_DCR.json` or `dcr.json`) |
| `ccf_config_file` | GitHub URL to the CCF configuration file (populated for CCF and CCF Push connectors; empty for CCF Legacy) |
| `ccf_capabilities` | Semicolon-separated list of CCF capabilities extracted from the config file or embedded pollingConfig (e.g., `APIKey;Paging;POST`) |

> **Key Design Decisions:**
> - **Azure Diagnostics > CCF name**: Connectors with `_CCP` suffix that reference "AzureDiagnostics" are Azure Diagnostics (the CCP suffix indicates the connector was built using the CCF framework, but it still collects via Azure Diagnostics)
> - **CCF content > Azure Function content**: Connectors with `dcrConfig`/`dataConnectorDefinitions` that also have "Deploy Azure Function" patterns are CCF (e.g., OktaSSOv2)
> - **Azure Function filename is strong**: Connectors with "FunctionApp" in the filename are Azure Functions regardless of content patterns
> - **Title-based AMA/MMA is strongest**: When a connector title explicitly includes "AMA" or "Legacy Agent", it overrides all other patterns
> - **MMA content patterns override AMA metadata**: MMA-era patterns like `OmsSolutions` and `InstallAgent*` take precedence over AMA detection from table metadata
> - **CCF suppresses sibling-ARM `Azure Function`**: The sibling-ARM-template scan (NordPass/Dataminr pattern) discovers Function App + DCR / Log Ingestion API resources and adds `Azure Function` to the method list. When the connector has already self-identified as `CCF` / `CCF Push` / `CCF (Legacy)`, the `Azure Function` method addition is suppressed: CCF v2 deployments include a Function App as the codeless-platform's poller runner, but from the customer's perspective the connector is still CCF. The API and per-table attribution from the ARM scan are still recorded.
> - **`Azure Function (TI Upload API)` supersedes generic REST**: When a connector is reclassified as `Azure Function (TI Upload API)` (via connector-code patterns, the `_UploadIndicatorsAPI` filename suffix, or an override), any pre-existing `REST Pull API` / `REST Push API` methods are dropped from the method list — TI Upload API is a specific Sentinel management-plane REST push, so the generic REST label is redundant.

#### Table-Level `collection_method` Resolution

`tables.csv` has its own `collection_method` column, resolved per table in this order. The first rule that yields a non-empty value wins, except for the tenant-diagnostics override (step 10) which can also overwrite a connector-inferred `Native`. Override-CSV entries (step 11) are applied last and overwrite whatever the resolver produced.

1. **ASIM short-circuit** — any table whose name starts with `ASim` / `_ASim` / `_Im_` (case-insensitive) is classified as `Various`. ASIM is a normalization layer that aggregates events from many heterogeneous sources, so a single "collection method" is not meaningful.
2. **Intrinsic value** from `tables_reference.csv` `collection_method` column (e.g. `AMA` for tables with VM resource types).
3. **Defender XDR override** — `source_defender_xdr=Yes` → `Defender`.
4. **Inherited from feeding connectors** when all of them use a single distinct informative method (1:1 method relationship across all connectors that ingest the table). Connector `collection_method` values are atomized on `|` before set comparison, so a connector declaring `CCF|Azure Function` contributes both methods.
5. **Published-connector trump** — if step 4 finds disagreement but the table is fed by both published (marketplace) and unpublished connectors, only the published connectors’ methods are kept. If that yields a single distinct method, it is used.
6. **Precedence collapse** when feeding connectors still disagree and the disagreement is a known generation overlap. Newer / canonical technology wins, applied iteratively until no further collapse is possible:

   | Co-feeding methods | Inferred method |
   |:-------------------|:----------------|
   | `AMA` + `MMA` | `AMA` |
   | `CCF` + `CCF (Legacy)` | `CCF` |
   | `Azure Function` + `CCF` | `CCF` |

7. **Azure Resources category** — table category includes `Azure Resources` → `Azure Diagnostics`.
8. **Resource-types fallback** — `tables_reference.resource_types` is non-empty (and not the `-` placeholder) → `Azure Diagnostics` (`method_source = resource_types`).
9. **`source_azure_monitor=Yes` fallback** — any table documented as an Azure Monitor table without a more specific signal → `Azure Diagnostics` (catches App Insights / Microsoft Graph / Entra B2C / Intune tables that lack `resource_types`).
10. **`_CL` last-resort fallback** — table name ends with `_CL` and nothing else attributed it → `Custom` (umbrella label intentionally distinct from `CCF`; covers Customer CCF and Log Ingestion API custom logs which cannot be distinguished from the public data).
11. **Tenant-diagnostics override** — fires when the current value is empty *or* `Native`. Triggers if either:
    - the table's `category` set intersects `{Entra, Intune, Microsoft Graph, Azure Active Directory}`, or
    - every `resource_types` token starts with a tenant-scope provider prefix (`microsoft.aadiam`, `microsoft.aad/domainservices`, `microsoft.azureadgraph`, `microsoft.intune`, `microsoft.aadcustomsecurityattributes`).

    These tables are delivered via Entra/Intune/Graph tenant Diagnostic Settings, not the ARM connector. The override corrects `Native` inferred from connectors (e.g. `AzureActiveDirectory`) whose ARM `dataTypes` list these tables but which actually configure a tenant diagnostic setting. The constants live at the top of `map_solutions_connectors_tables.py` (`TENANT_DIAGNOSTICS_CATEGORIES`, `TENANT_DIAGNOSTICS_RESOURCE_PREFIXES`).
12. **Normalization** — `_normalize_collection_method` lowercases-then-canonicalizes (`native` → `Native`, legacy `MMA` → `AMA`) and `_collapse_parenthesized_refinement` collapses pipe-multivalues like `Azure Function (TI Upload API)|Azure Function` to the canonical base.
13. **Override CSV (last)** — entries in `solution_analyzer_overrides.csv` with `Entity=Table` and `Field=collection_method` are applied to `tables.csv` rows after resolution. Used for tables that need explicit classification independent of resolver behavior — for example, `SecurityAlert` and `SecurityIncident` are marked `Internal` because the `MicrosoftThreatProtection` connector's ARM `dataTypes` list includes them but Sentinel produces them internally.

Comparisons are case-insensitive throughout.

**Diagnostic columns recorded on every row of `tables.csv`:**

| Column | Description |
|--------|-------------|
| `collection_method_source` | How the value was resolved. One of: `asim_table`, `tables_reference`, `source_defender_xdr`, `connector`, `connector_published_only`, `connector_precedence({rule trail})`, `category=Azure Resources`, `resource_types`, `source_azure_monitor`, `cl_table_fallback`, `tenant_diagnostics(category=...)`, `tenant_diagnostics(resource_types)`. Override-CSV writes do **not** update this column — the source reflects the resolver's last decision. |
| `collection_method_candidates` | Comma-separated set of distinct atomized methods seen across feeding connectors (or `Various` for ASIM tables). |
| `feeding_connector_ids` | Comma-separated IDs of every connector that ingests the table, for traceability. |

**Findings are surfaced in the unified exceptions report.** Disagreements and unresolved cases are written to [`solutions_connectors_tables_issues_and_exceptions_report.csv`](csv/solutions_connectors_tables_issues_and_exceptions_report.md) (no separate CSVs):

| `reason` | Trigger |
|----------|---------|
| `table_method_conflict` | Intrinsic value disagrees with the connector-inferred (or precedence-collapsed) method. Intrinsic always wins; the disagreement is logged for visibility. The `details` column lists the intrinsic value, its source, the connector-inferred method, and the feeding connector IDs. |
| `table_method_ambiguity` | Feeding connectors still disagree after the published-trump filter and precedence collapse, **and** no intrinsic value was set. The `details` column lists the candidate methods and a `method:[connector_id,...]` breakdown. Tables that already have an intrinsic value (e.g. `Syslog`, `CommonSecurityLog` → `AMA`) are not reported here since the intrinsic wins. |

### CCF Configuration and Capabilities

For connectors detected as **CCF** or **CCF Push**, the analyzer locates the CCF configuration file and extracts capabilities from it. For **CCF (Legacy)** connectors, capabilities are extracted from the embedded `pollingConfig`.

#### CCF Config File Discovery

The analyzer searches the connector's directory (and sibling `*_ccp/` directories) for files matching these patterns (in order):
- `*PollingConfig*.json`, `*PollerConfig*.json` — standard CCF poller configs
- `*DataConnectorPoller*.json`, `*dataPoller*.json` — alternative naming
- `*_poller*.json` — older naming convention
- `connectors.json` — modern CCF naming (e.g., Bitwarden)
- `*_dataConnector*.json` (excluding `*connectorDefinition*`) — Push connector configs
- Sibling `*_ccp/` directories — some connectors (e.g., GCP) store configs in a sibling directory with `_ccp` suffix

Files matching skip patterns are excluded: `azuredeploy*`, `mainTemplate*`, `*connectorDefinition*`, `definitions.json`, `*_table.*`, `*_dcr.*`, and common non-config files.

If no separate config file is found but `pollingConfig` exists in the primary connector JSON, the connector is reclassified as **CCF (Legacy)** and capabilities are extracted from the embedded config.

#### CCF Capabilities Extracted

| Capability | Description |
|-----------|-------------|
| **Connector Kind** | Non-default kinds: `GCP`, `AmazonWebServicesS3`, `Push`, `StorageAccountBlobContainer`, `WebSocket`, `OCI`, etc. (`RestApiPoller` is omitted as it's the default) |
| **Auth Type** | Authentication method: `APIKey`, `OAuth2`, `Basic`, `JwtToken`, `Push`, `ServicePrincipal`, `Session`, etc. |
| `Paging` | Whether the connector uses paging to retrieve results |
| `POST` | Whether the connector uses HTTP POST (GET is the default) |
| `MvExpand` | Whether the config uses the MvExpand transformer (`nestedTransformName` containing `MvExpandTransformer`) |
| `Nested` | Whether the config uses nested steps (`stepType: Nested`) |

### Ingestion API Detection

For API-based connectors (CCF Push, Azure Function, REST API, Unknown Custom Log), the analyzer determines whether they use the modern **Log Ingestion API** or the legacy **HTTP Data Collector API** (also known as Log Analytics Data Collector API). CCF and CCF (Legacy) connectors are excluded because their ingestion is platform-managed (Sentinel PaaS) — the connector definition doesn't configure the ingestion API.

This analysis runs in a second pass after table schemas are fully loaded, because the column suffix heuristic requires schema data.

#### Detection Rules (in priority order)

1. **CCF Push** → Always **Log Ingestion API** (DCR-based, solution code pushes data via DCR)
2. **Azure Function** → Scan `*.py` files in the solution's Data Connectors folder for API-specific patterns (excluding vendored directories like `.python_packages`):
   - Log Ingestion API indicators: `LogsIngestionClient`, `azure.monitor.ingestion`, `azure-monitor-ingestion`, `ingestion_endpoint`, `DCR_ID`, `RULE_ID`, `data_collection_rule`
   - HTTP Data Collector API indicators: `SharedKey`, `build_signature`, `api/logs`, `Log-Type`, `LogAnalyticsData`
   - If both detected → "Undetermined" (typically indicates migration in progress)
3. **REST API / Unknown (Custom Log)** → Scan connector JSON for workspace key patterns: `sharedKeys`, `WorkspaceId`, `PrimaryKey` → **HTTP Data Collector API**
4. **Fallback** → Table column suffix heuristic:
   - If >40% of table columns end with type suffixes (`_s`, `_d`, `_b`, `_t`, `_g`) → **HTTP Data Collector API**
   - If table has DCR-sourced schema and <10% type suffixes → **Log Ingestion API**

#### CSV Fields Affected

| Field | Description |
|-------|-------------|
| `ingestion_api` | Detected API: "Log Ingestion API", "HTTP Data Collector API", "Undetermined", or empty if not applicable |
| `ingestion_api_reason` | Human-readable reason for the detection (e.g., "CCF connectors use DCR-based Log Ingestion API") |

### Custom Log V1 (CLv1) Detection

The analyzer identifies tables using the legacy **Custom Log V1** schema format. These are custom log tables originally created through the HTTP Data Collector API, which automatically appends type suffixes (`_s`, `_d`, `_b`, `_t`, `_g`) to column names to indicate data types.

This detection runs after both table schemas and ingestion API detection are complete.

#### Detection Rules

A table is marked as CLv1 (`is_clv1 = true`) if **either** condition is met:

1. **Column suffix heuristic** — More than 40% of the table's non-standard columns end with type suffixes (`_s`, `_d`, `_b`, `_t`, `_g`). Standard columns excluded from the count: `TimeGenerated`, `TenantId`, `Type`, `MG`, `ManagementGroupName`, `SourceSystem`, `_ResourceId`, `_SubscriptionId`.

2. **Connector-based inference** — The table name ends with `_CL` (custom log) AND at least one connector that ingests into this table uses the **HTTP Data Collector API** ingestion API
   
   **Exception:** If the table has schema data in `table_schemas_lookup` and none of the non-standard columns have type suffixes, the connector-based rule is skipped. This prevents false positives for tables that have both a legacy connector and a modern connector (e.g., CrowdStrike tables served by both an Azure Function HTTP Collector connector and a CCF connector).

A connector is marked as CLv1 if **any** of its tables are CLv1.

#### CSV Fields Affected

| Field | CSV File | Description |
|-------|----------|-------------|
| `is_clv1` | `tables.csv` | `true` if the table uses CLv1 schema format |
| `is_clv1` | `connectors.csv` | `true` if any of the connector's tables use CLv1 schema format |

### Filter Fields Detection

The analyzer extracts filter field values from KQL queries to identify vendor/product-specific filtering patterns. This helps understand which data sources a connector, parser, or content item targets.

#### Supported Filter Fields

| Field | Canonical Table | Description |
|-------|----------------|-------------|
| `DeviceVendor` | CommonSecurityLog | CEF vendor identifier |
| `DeviceProduct` | CommonSecurityLog | CEF product identifier |
| `DeviceEventClassID` | CommonSecurityLog | CEF event class identifier |
| `EventVendor` | Multiple (ASIM) | ASIM normalized vendor |
| `EventProduct` | Multiple (ASIM) | ASIM normalized product |
| `EventType` | Multiple (ASIM) | ASIM normalized event type |
| `ResourceType` | AzureDiagnostics | Azure resource type |
| `Category` | AzureDiagnostics | Diagnostic category |
| `Resource` | AzureDiagnostics/AzureMetrics/AzureActivity | Azure resource instance name |
| `ResourceProvider` | AzureActivity | Azure resource provider |
| `EventID` | WindowsEvent/SecurityEvent/Event | Windows event ID |
| `Source` | Event | Windows Event Log source |
| `Provider` | WindowsEvent | Windows event provider |
| `Facility` | Syslog | Syslog facility |
| `ProcessName` | Syslog | Syslog process name |
| `ProcessID` | Syslog | Syslog process ID |
| `SyslogMessage` | Syslog | Syslog message content |
| `EventName` | AWSCloudTrail | AWS API event name |
| `ActionType` | DeviceEvents/DeviceFileEvents/etc. | Microsoft Defender XDR action type |
| `OperationName` | AuditLogs/AzureActivity/OfficeActivity/SigninLogs | Azure/M365 operation name |
| `OfficeWorkload` | OfficeActivity | Office 365 workload type |
| `RecordType` | OfficeActivity | Office 365 record type (numeric) |

#### Supported Operators

| Operator Category | Operators | Example |
|-------------------|-----------|---------|
| **Equality** | `==`, `=~`, `!=` | `DeviceVendor == "Fortinet"` |
| **In operators** | `in`, `in~`, `!in`, `!in~` | `EventID in (4624, 4625)` |
| **String operators** | `has`, `has_any`, `has_all`, `contains`, `startswith`, `endswith` | `SyslogMessage has "error"` |
| **Negative string** | `!has`, `!contains`, `!startswith`, `!endswith` | `SyslogMessage !has "debug"` |
| **Case-sensitive** | `has_cs`, `contains_cs`, `startswith_cs`, `endswith_cs` | `ProcessName has_cs "sshd"` |

> **Note:** `EventID`, `ProcessID`, and `RecordType` fields only support equality and in operators, not string operators.

#### Detection Logic

Filter field extraction runs in two complementary passes. The first pass is **table-aware**: it dispatches each curated field to a target table using the rules in [`filter_field_resolution.yaml`](../filter_field_resolution.yaml). The YAML supports five rule types:

| Rule type | Semantics |
|-----------|-----------|
| `direct` | Field always attributes to a fixed table (e.g. `DeviceVendor` → `CommonSecurityLog`). |
| `gated` | Field attributes to the configured table only if that table appears in the query (e.g. `Facility` → `Syslog` only when `Syslog` is referenced). |
| `priority` | Try each candidate table in order; pick the first one present in the query's tables (e.g. `EventID` → `WindowsEvent` > `SecurityEvent` > `Event`). |
| `any_of` | Pick any candidate that appears; with `prefer_local: true`, prefer tables in the current sub-query over global tables. |
| `prefix` | Pick the first query table whose name starts with a tag from `prefix_groups` (e.g. `EventVendor` → first table whose name starts with `asim`/`_asim`/`_im_`). |

An optional `skip_flag` on a field references a boolean from the calling context. When set, the field is skipped entirely — used for ASIM parsers, which `extend` `EventVendor`/`EventProduct` rather than filter on them. Editing the YAML changes filter-field attribution without touching the script.

**Pass 1 — curated whitelist (table-aware).** The fields configured in `filter_field_resolution.yaml` are matched against KQL where-predicates and dispatched per the rules above:

   - `DeviceVendor`/`DeviceProduct`/`DeviceEventClassID` → CommonSecurityLog
   - `EventVendor`/`EventProduct`/`EventType` → Context-dependent (ASIM tables)
   - `ResourceType`/`Category` → AzureDiagnostics
   - `Resource` → AzureDiagnostics, AzureMetrics, or AzureActivity (based on which is in query)
   - `ResourceProvider` → AzureActivity
   - `EventID` → WindowsEvent, SecurityEvent, or Event (based on which is in query)
   - `Source` → Event
   - `Provider` → WindowsEvent
   - `Facility`/`ProcessName`/`ProcessID`/`SyslogMessage` → Syslog
   - `EventName` → AWSCloudTrail
   - `ActionType` → DeviceEvents, DeviceFileEvents, DeviceProcessEvents, etc. (MDE/XDR tables)
   - `OperationName` → AuditLogs, AzureActivity, OfficeActivity, SigninLogs (context-dependent)
   - `OfficeWorkload`/`RecordType` → OfficeActivity

**Pass 2 — schema-driven (any documented column).** After the whitelist pass, a generic pass extracts any other where-predicate field that is either:

   - a documented column of a table the query references — looked up in `la_table_schemas.csv` (Azure Monitor / Defender XDR docs) and `asim_fields.csv` (ASIM normalized fields). The field is attributed to the referenced table only when ownership is unambiguous.
   - defined earlier in the same query via `| extend Name = ...` — these are recorded under the synthetic table name `_Computed` (e.g. `_Computed.AccountName == "x"`) so consumers can distinguish derived-field selection from raw-column selection.

   Before the generic pass runs, `let X = ...;` blocks are stripped so their RHS literals don't masquerade as where-predicates. Identifiers that match KQL reserved words are skipped.

**Common rules (both passes):**

3. **ASIM vendor/product skipping**: When `skip_asim_vendor_product=True`, `EventVendor` and `EventProduct` are skipped because ASIM parsers SET these values (not filter by them).

4. **Context filtering**: The extractor skips fields that appear in:
   - `extend` statements on the same pipe segment (those are field definitions; their *uses* in subsequent `where` clauses are recorded under `_Computed`)
   - `project` statements (output field definitions)
   - Line comments (`//`)
   - Block comments (`/* */`)

5. **In operator value extraction**: Literal values in `in` operators are parsed, supporting:
   - String literals: `in ("value1", "value2")`
   - Integer literals: `in (4624, 4625, 4634)`
   - Case-insensitive: `in~` variant
   - Variable resolution: `let EventList = dynamic([...])` then `EventName in~ (EventList)`

6. **String operator patterns**: Match patterns like `field has "value"` or `field has_any ("val1", "val2")`

7. **Operator folding**: Multiple equality operators for the same field are combined:
   - Multiple `==` values → single `in` operator with comma-separated values
   - Multiple `=~` values → single `in~` operator
   - Case-insensitive values take precedence over case-sensitive for deduplication

8. **Parser-call inheritance (connectors only).** When a connector's extracted query (e.g. `baseQuery`, `lastDataReceivedQuery`, `connectivityCriteria`) is just a vendor parser-function call — `ClarotyEvent`, `CiscoSEGEvent`, `IllumioCoreEvent`, `OSSECEvent`, `NetwrixAuditor`, `PingFederateEvent`, etc. — neither pass would normally extract any predicates because the leading identifier is a parser, not a documented table. To recover the connector's true selection criteria, a third pass resolves the leading identifier against `parsers.csv` and `asim_parsers.csv` (also keyed by ASIM `equivalent_builtin` aliases) and merges the parser's `filter_fields` predicates onto the connector. Without this pass, such connectors had empty `filter_fields` and the "unfiltered connector matches every target on a shared table" rule produced spurious connector ↔ ASIM-parser / content-item associations.

#### Output Format

Filter fields are formatted as a pipe-separated (`|`) list with the structure:
```
Table.Field operator "value" | Table.Field operator "value1,value2"
```

Computed (extend-derived) fields use the synthetic table name `_Computed`:
```
_Computed.AccountName == "Anonymous" | _Computed.LogType in "firewall,vpn_firewall"
```

Examples:
```
CommonSecurityLog.DeviceVendor == "Fortinet" | CommonSecurityLog.DeviceProduct == "FortiGate"
AwsSecurityHubFindings.RecordState == "ACTIVE" | AwsSecurityHubFindings.ComplianceStatus == "FAILED"
Syslog.Facility == "authpriv" | Syslog.SyslogMessage has "error"
AzureDiagnostics.Category in "AzureFirewallNetworkRule,AzureFirewallApplicationRule"
AWSCloudTrail.EventName in~ "CreateUser,DeleteUser,AttachUserPolicy"
```

#### CSV Fields Affected

| CSV File | Field | Description |
|----------|-------|-------------|
| `connectors.csv` | `filter_fields` | Filter fields from connector queries |
| `connectors.csv` | `event_vendor` | Extracted vendor values (semicolon-separated) |
| `connectors.csv` | `event_product` | Extracted product values (semicolon-separated) |
| `connectors.csv` | `event_vendor_product_by_table` | JSON mapping of tables to vendor/product pairs |
| `content_items.csv` | `content_filter_fields` | Filter fields from content item queries |
| `content_items.csv` | `content_event_vendor` | Extracted vendor values |
| `content_items.csv` | `content_event_product` | Extracted product values |
| `parsers.csv` | `filter_fields` | Filter fields from solution parser queries |
| `asim_parsers.csv` | `filter_fields` | Filter fields from ASIM parser queries |

> **Note:** For ASIM parsers, `EventVendor` and `EventProduct` fields are skipped because ASIM parsers SET these values (via `extend`) rather than filter by them. The extraction focuses on source-identifying fields like `DeviceVendor`, `Facility`, etc.

### Connector Association Algorithm

For standalone/GitHub Only content items and ASIM parsers, the analyzer automatically associates relevant connectors based on table and filter field matching. This populates the `associated_connectors` and `associated_solutions` fields.

#### Matching Criteria

A connector matches a target (content item or parser) if:

1. **Shared Tables**: The connector and target share at least one table
2. **Filter Subset**: For shared tables, the connector's filter values are a subset of (or equal to) the target's filter values

#### Filter Subset Logic

- A connector with **no filter fields** matches any target using the same table (it provides all data)
- A connector filtering on `DeviceVendor == "Fortinet"` matches targets filtering on `Fortinet` or `Fortinet AND FortiGate`
- A connector filtering on specific products does NOT match targets filtering on different products

#### Cross-Field Override: Category → ResourceType

For AzureDiagnostics, certain `Category` values are known to be produced only by a specific Azure resource type. When a connector filters on `ResourceType` and the target only filters on `Category`, the `CATEGORY_TO_RESOURCE_TYPE` mapping is consulted: if all of the target's Category values map to the connector's ResourceType, the match is allowed (the target is more restrictive).

Currently mapped categories:

| Category | ResourceType |
|----------|-------------|
| `AzureFirewallNetworkRule` | `AZUREFIREWALLS` |
| `AzureFirewallApplicationRule` | `AZUREFIREWALLS` |
| `AzureFirewallNatRule` | `AZUREFIREWALLS` |
| `AzureFirewallThreatIntel` | `AZUREFIREWALLS` |
| `AzureFirewallIdpsSignature` | `AZUREFIREWALLS` |
| `AzureFirewallDnsProxy` | `AZUREFIREWALLS` |

This mapping can be extended for other Azure resource types as needed.

#### Example Matches

| Connector Filters | Target Filters | Match? | Reason |
|-------------------|----------------|--------|--------|
| (none) | `DeviceVendor == "Fortinet"` | ✅ | Connector provides all data |
| `DeviceVendor == "Fortinet"` | `DeviceVendor == "Fortinet"` | ✅ | Exact match |
| `DeviceVendor == "Fortinet"` | `DeviceVendor in "Fortinet,PaloAlto"` | ✅ | Connector subset of target |
| `DeviceVendor == "Fortinet"` | `DeviceVendor == "PaloAlto"` | ❌ | No overlap |
| `DeviceProduct == "FortiGate"` | `DeviceVendor == "Fortinet"` | ❌ | Different field, can't confirm match |
| `ResourceType == "AZUREFIREWALLS"` | `Category == "AzureFirewallNetworkRule"` | ✅ | Category implies ResourceType (override) |

#### Exclusions

The algorithm excludes:
- **Content-only connectors**: Connectors that use data from other connectors (don't ingest data themselves)
- **Excluded tables**: Tables that appear in connector documentation but aren't actually ingested

> Deprecated connectors (`is_deprecated=true` — `[DEPRECATED]` in title, `availability.status: 0`, or inherited from a deprecated parent solution) are **not** excluded from association. They still appear in `associated_connectors` of any target whose selection criteria they satisfy, so the original connector for a parser/content item remains visible after deprecation. The `is_deprecated` flag on the connector row remains the indicator.

### Parser Resolution

When a connector references a parser function (e.g., `ASimDns`):
1. Script locates the parser YAML file in the solution's Parsers directory
2. Extracts the FunctionQuery from the parser
3. Analyzes the query to find actual table references (e.g., `Syslog`, `DnsEvents`)
4. Maps the parser name to the discovered tables
5. Replaces parser reference with actual tables in the output

### Connector Table Source Priority

For each connector, tables are gathered from several sources. The most authoritative source for what a connector *ingests* is its Data Collection Rule (DCR) and table-definition companion files, so the analyzer applies the following priority:

1. **`dataTypes` declarations** in the connector definition.
2. **Companion `*_Table.json` / `*_DCR.json` files** in the connector's folder (`find_companion_table_files`). The DCR's output stream (e.g., `Custom-OktaV2_CL`) and the table definition declare exactly what the connector writes to.
3. **Query analysis** of the connector's UI/status queries (`graphQueries`, `sampleQueries`, `lastDataReceivedQuery`, connectivity criteria), including expansion of any parser functions they reference.

**The DCR/Table companion files trump query analysis.** When companion `*_Table.json` / `*_DCR.json` files are present for a connector, the analyzer treats them as ground truth and **skips query analysis** (priority 3) entirely for that connector. This prevents non-ingested tables from leaking onto the connector.

> **Why this matters:** Connector status queries such as `lastDataReceivedQuery` frequently call a shared parser that `union`s multiple tables, including legacy ones. For example, a CCF v2 connector whose DCR writes only `OktaV2_CL` may run a status query through a parser that unions both `OktaV2_CL` and the legacy `Okta_CL`. Without this rule, query analysis would incorrectly attach `Okta_CL` to the v2 connector. Because the connector ships an authoritative `*_DCR.json` (output stream `Custom-OktaV2_CL`) and `*_Tables.json`, query analysis is skipped and only `OktaV2_CL` is mapped.

Connectors that do **not** ship companion DCR/Table files (e.g., older Azure Function connectors) continue to rely on query analysis as before.

### Table Detection Methods

The analyzer uses a unified KQL query parsing engine (`extract_query_table_tokens()`) to identify tables across all source types: connectors, content items, and parsers. This ensures consistent table detection regardless of the source.

#### Detection Sources by Type

| Source Type | Query Locations | Additional Processing |
|-------------|-----------------|----------------------|
| **Connectors** | `graphQueries.*.baseQuery`, `sampleQueries.*.query`, `dataTypes.*.lastDataReceivedQuery`, `connectivityCriteria.*.value` (CCF v3 singular) and `connectivityCriterias.*.value` (legacy plural), ARM template variables. Query-bearing fields are read from the top-level JSON, from `properties.connectorUiConfig` (CCF v3 `connectorDefinition`), and from `resources[*].properties.connectorUiConfig` (CCF ARM templates). | Parser expansion, dataType name/query reconciliation |
| **Content Items** | YAML `query` field, JSON `query` field | ASIM parsers kept as-is, non-ASIM parsers expanded |
| **Solution Parsers** | `FunctionQuery` (YAML), raw query text (.kql/.txt) | Tables extracted, parser names recorded |
| **ASIM Parsers** | `ParserQuery` (YAML) | Sub-parser references tracked separately |

#### Table Detection Method Labels

When enabled with `--show-detection-methods`, the `table_detection_methods` column shows exactly how each table was detected:

| Method Label | Description |
|--------------|-------------|
| `graphQueries.{index}.baseQuery` | From connector graphQueries array |
| `sampleQueries.{index}.query` | From connector sampleQueries array |
| `dataTypes.{index}.lastDataReceivedQuery` | From dataTypes definitions |
| `dataTypes.{index}.name` | From dataTypes name field (when query missing). Supports the `Table(Qualifier)` pattern (e.g., `Event(ThreatIntelligenceIndicator)`) by extracting the inner qualifier as the table name when no query is available. |
| `connectivityCriterias.{index}.value.{sub_index}` | From connectivity criteria queries |
| `logAnalyticsTableId` | Extracted from ARM template variables |
| `parser:{parser_name}` | Resolved from parser function to actual table |

### Context-Aware Table Detection

The KQL parser uses intelligent query parsing to distinguish actual table names from field names and variables:

#### Parsing Techniques

| Technique | Description |
|-----------|-------------|
| **Let Assignment Tracking** | Tracks `let var = TableName` assignments to avoid treating variables as tables |
| **Pipeline Head Detection** | Identifies tables at the start of pipeline expressions (`TableName \| where...`) |
| **Union Statement Parsing** | Extracts all table names from `union` expressions with comma or parenthesis separators |
| **Inline Pipe Detection** | Handles `TableName \| where` patterns on the same line |
| **Parenthesis/Brace Context** | Detects tables in `(TableName \| ...)` and `{ TableName \| ...}` patterns |
| **ASIM View Detection** | Recognizes `_Im_*` and `_ASim_*` function calls; these are kept as-is (not expanded to underlying tables) but filtered out during validation since they are parser functions, not physical tables |
| **Comment Stripping** | Removes `//` line comments before analysis |
| **Field Context Filtering** | Excludes identifiers after `\| project`, `\| project-keep`, `\| project-reorder`, `\| extend`, `\| parse` operators |

#### Table Validation

All candidates are filtered through `is_valid_table_candidate()` which:
- Accepts known Azure Monitor tables (from reference data), including real ASIM log tables (e.g., `ASimAuditEventLogs`)
- Accepts custom log tables (ending in `_CL`)
- Rejects ASIM parser function names (e.g., `ASimAuditEvent`, `imDns`, `_Im_Dns`) since they are not physical tables
- Accepts known parser names (when provided)
- Rejects KQL keywords, operators, and common false positives

### JSON Parsing Tolerance

The analyzer includes enhanced JSON parsing to handle common issues in ARM templates:

- Strips `// comments` from JSON (common in ARM templates)
- Removes trailing commas before `}` or `]`
- Falls back to json5 parser if available for even more tolerance

## Examples

### Example 1: Simple Connector
A connector directly references `Syslog` table in its queries:
```
Table: Syslog
solution_name: ISC Bind
connector_id: ISCBind
table_detection_methods: sampleQueries.0.query;sampleQueries.1.query
```

### Example 2: Parser-Based Connector
A connector references a parser that resolves to actual tables:
```
Table: Syslog
solution_name: Watchguard Firebox
connector_id: WatchguardFirebox
table_detection_methods: parser:WatchGuardFirebox
```

### Example 3: Multiple Tables
A connector ingests to multiple custom log tables:
```
Table: CyfirmaASCertificatesAlerts_CL
solution_name: Cyfirma Cyber Intelligence
connector_id: CyfirmaCyberIntelligence
```

## Troubleshooting

### Common Issues

**Issue**: Script reports "Permission denied" when writing CSV
- **Solution**: Close the CSV file if open in Excel or another application

**Issue**: Some connectors missing from output
- **Solution**: Check the report CSV for the reason (likely no_table_definitions or parser_tables_only)

**Issue**: Parser tables not resolving
- **Solution**: Ensure parser YAML files exist in the solution's Parsers directory with valid FunctionQuery

**Issue**: JSON parse errors for specific connectors
- **Solution**: Install json5 (`pip install json5`) for better tolerance, or fix JSON syntax in the connector file

### Debug Mode

To see which files are being processed:
```bash
python map_solutions_connectors_tables.py --show-detection-methods
```

This will include the `table_detection_methods` column showing exactly how each table was detected.
