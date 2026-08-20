---
name: asim-parser-filter-validator
description: Validates ASIM parser filtering parameters by running filter tests against a Log Analytics workspace. Pure PowerShell using az CLI for authentication — no Python or Azure SDK packages required. Use this skill after creating or modifying an ASIM parser to verify that its filtering parameters work correctly.
requiredSkills:
  - az-cli-command-runner
---

# ASIM Parser Filter Validator

Validates that an ASIM parser's filtering parameters (e.g. `disabled`, `starttime`, `endtime`, `srcipaddr_has_any_prefix`, etc.) behave correctly by running queries against a Log Analytics workspace.

This skill is a **pure PowerShell** implementation that uses `az CLI` for authentication. No Python, Azure SDK packages, or YAML modules are required.

- **PowerShell 7+**
- **Azure CLI** (logged in via `az login`)

## What it tests

For every filtering parameter declared in the parser's KQL function signature:

| Parameter type                                           | Tests performed                                                                                                                           |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `disabled`                                               | `disabled=true` returns 0 rows; `disabled=false` returns rows                                                                             |
| `datetime` (`starttime` / `endtime`)                     | Filtering by the midpoint timestamp returns fewer rows than unfiltered                                                                    |
| Scalar (`string`, `int`)                                 | Filtering by a real value returns exactly that value; filtering by a fictitious value returns 0 rows                                      |
| `dynamic` (`*_has_any`, `*_has_all`, `*_has_any_prefix`) | Filtering by one/two real values returns fewer rows; fictitious value returns 0 rows; substring / prefix variants tested where applicable |

## Supported schemas

AgentEvent, AlertEvent, AssetEntity, AuditEvent, Authentication, DhcpEvent, Dns, FileEvent, NetworkSession, ProcessEvent, RegistryEvent, UserManagement, WebSession.

## Inputs

| Input           | Required | Description                                                       |
| --------------- | -------- | ----------------------------------------------------------------- |
| Parser KQL path | Yes      | Path to the ASIM parser `.kql` file to test                       |
| Schema name     | Yes      | ASIM schema name (e.g. `Dns`, `Authentication`, `NetworkSession`) |
| Workspace ID    | Yes      | Log Analytics workspace GUID to run queries against               |

## How to run

```powershell
.\scripts\asimFilterTest.ps1 -ParserFile "{PathToFilterParserKQL}" -SchemaName "{SchemaName}" -WorkspaceId "{your-workspace-guid}"
```

## Prerequisites

1. **Azure CLI authenticated** — run `az login` if not already logged in. If you get an authentication error, use the `az-cli-command-runner` skill to verify login status.
2. The workspace must contain data for the tables referenced by the parser.

## Interpreting results

- **Green** — test passed.
- **FAIL** — the filtering parameter did not behave as expected. The failure message indicates which parameter failed and what was expected.
- **Known partial validations** — AuditEvent (`EventResult`), Authentication (`EventType`), and Dns (`EventType`) have known single-failure scenarios that are automatically ignored.

### Known acceptable failure reasons (can be ignored)

When analyzing filter-validation failures, a failure can be **ignored** if it matches one of these inherent-limitation categories:

1. **Documented schema known exception** — The schema defines a known exception for a parameter (e.g. a multi-value test that cannot succeed because the value combinations do not co-exist in that schema's data). Check whether the ASIM schema documentation lists the parameter as a known exception.
2. **Constant or single-value field by design** — The parser maps the filtered field to a single constant value, so multi-value or reduction-based filtering cannot reduce rows further. This is expected when the source provides only one possible value for that field.
3. **Insufficient distinct values in the test window** — The 2-day query window does not contain enough distinct values for the field to exercise multi-value filtering. This is a data-availability limitation, not a parser bug.

When reviewing filter-validation output, analyze each failure message against these categories. If **all other parameters pass** and every failure maps to one of the reasons above, the parser's filtering implementation is considered correct.

## Troubleshooting

| Symptom                                     | Fix                                                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `Failed to acquire access token via az CLI` | Run `az login`                                                                                                      |
| `No data in the provided workspace`         | Ensure the workspace has ingested data for the relevant tables within the last 2 days                               |
| `Schema: X - Not supported`                 | The schema name is not in the supported list — update the `$AllSchemasParameters` hashtable in `asimFilterTest.ps1` |
