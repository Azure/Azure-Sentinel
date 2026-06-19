---
name: asim-parser-validator
description: This skill will validate an ASIM by checking the schema output of the parser and also checking the data that the parser represents in the columns. Use this skill after you have created or updated an ASIM parser to validate that the parser is correctly mapping the source data to the ASIM schema.
requiredSkills:
  - az-cli-command-runner
  - log-analytics-workspace-queryer
---

# Validation functions

There are two validations that will need to be run against the ASIM parser:

1. **Schema validation:** Checks that the output of the ASIM parser has the correct columns and data types matching the ASIM schema.
2. **Data validation:** Checks that the values in the columns are correctly mapped and transformed — including enumerations, data type formatting (e.g., IP addresses), and value normalization.

## Inputs

This skill requires the following:

- **ASIM parser KQL** — the full KQL query of the parser (or the file path to the `.kql` file).
- **ASIM schema name** — the target schema (e.g., `NetworkSession`, `Authentication`).
- **Workspace ID** — the Log Analytics workspace GUID where the parser will be tested.
- **Resource group** and **workspace name** — needed to check for existing saved searches. If not already known, use the `az-cli-command-runner` skill to find them:

```
az monitor log-analytics workspace list --query "[?customerId=='<workspaceId>'].{name:name, resourceGroup:resourceGroup}" -o json
```

All queries in this skill must be executed using the `log-analytics-workspace-queryer` skill.

## Step 0: Check if ASIM testers are already deployed

Before fetching the YAML files, check if `ASimSchemaTester` and `ASimDataTester` are already available as saved searches in the workspace. Use the `az-cli-command-runner` skill to run:

```
az monitor log-analytics workspace saved-search list --resource-group <rg> --workspace-name <name> --query "[].{functionAlias:functionAlias}" -o table
```

Look for entries with values `ASimSchemaTester` and `ASimDataTester` in the results.

- **If both functions exist** — skip the YAML fetch and inline function definition in Steps 1 and 2. Call the functions directly (see simplified queries below).
- **If either function is missing** — deploy the tester ARM templates to the workspace before proceeding:
  1. Download the ARM template JSON files:
     - https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/ASimSchemaTester.json
     - https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/ASimDataTester.json

  2. Use the `az-cli-command-runner` skill to deploy each template:

     ```
     az deployment group create --resource-group <resourceGroup> --template-file <templateFilePath> --parameters Workspace=<workspaceName> WorkspaceRegion=<location>
     ```

  3. After successful deployment, the functions are available in the workspace. Use the simplified direct call queries in Steps 1 and 2.

## Step 1: Schema validation (ASimSchemaTester)

Run the schema validation query:

```kql
<ASIM parser KQL> | getschema | invoke ASimSchemaTester("<name of the ASIM schema>")
```

### Interpreting schema validation results

Results fall into 3 severity levels:

- **`(0)` Error** — Must be fixed before proceeding. These indicate missing mandatory fields, type mismatches, or missing aliases.
- **`(1)` Warning** — Missing recommended fields. Attempt to fix, but do not brute-force a fix if the source data does not contain the information.
- **`(2)` Info** — Two sub-categories:
  - **"extra unnormalized column"** — The parser output contains columns not defined in the ASIM schema. Fix these by removing the extra columns from the parser output using `project`.
  - **All other Info messages** (e.g., missing optional fields/aliases) — Can be safely ignored.

**Address all errors before proceeding to Step 2.**

## Step 2: Data validation (ASimDataTester)

Run the data validation query. The `| limit 1000` restricts the number of rows inspected because the data tester evaluates individual row values, which is more expensive than schema-level checks.

```kql
<ASIM parser KQL> | limit 1000 | invoke ASimDataTester("<name of the ASIM schema>")
```

### Interpreting data validation results

- **Fix** errors related to enumerated fields — these indicate the parser is producing values that are not in the allowed set for that column.
- **Fix** errors related to data type formatting — these indicate values do not match the expected format (e.g., an IP address column contains non-IP values).

## Step 3: Verify the parser runs without syntax errors

After making fixes based on the validation results, run the modified parser KQL query by itself to confirm it executes without syntax errors:

```kql
<ASIM parser KQL>
```

If the query fails with a syntax error, fix the issue before returning results to the calling skill.

## Outputs

This skill returns the following to the calling skill or orchestrator:

- **Schema validation results** — the list of Error, Warning, and Info messages from `ASimSchemaTester`.
- **Data validation results** — the list of Error, Warning, and Info messages from `ASimDataTester`.
- **Summary** — whether any Error-level `(0)` results remain after both validations.
