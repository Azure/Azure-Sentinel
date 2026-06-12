---
name: asim-parser-validator
description: This skill will validate an ASIM by checking the schema output of the parser and also checking the data that the parser represents in the columns. Use this skill after you have created or updated an ASIM parser to validate that the parser is correctly mapping the source data to the ASIM schema.
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

All queries in this skill must be executed using the `log-analytics-workspace-queryer` skill.

## Step 1: Schema validation (ASimSchemaTester)

Define the `ASimSchemaTester` KQL function inline and run it as a **single combined query** — the inline function declaration, the parser KQL, and the `| getschema | invoke` call must all be part of one query sent to the workspace.

```kql
let ASimSchemaTester = (T:(ColumnName:string,ColumnType:string), selected_schema:string) {
let ASimFields = materialize(externaldata (ColumnName: string, ColumnType: string, Class: string, Schema: string, LogicalType:string, ListOfValues: string, AliasedField: string)
        [@"https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/ASIM/dev/ASimTester/ASimTester.csv"] with (format="csv", IgnoreFirstRecord=true)
        | where Schema =~ selected_schema);
    let ASimFieldsWithAliases = materialize(ASimFields | project-rename SchemaColumn = ColumnName, SchemaType = ColumnType | lookup (ASimFields | project ParentClass = Class, ParentColumn = ColumnName) on $left.AliasedField == $right.ParentColumn);
    let ParserFields = toscalar (T | summarize make_set(ColumnName));
    T
    | join kind=fullouter ASimFieldsWithAliases on $left.ColumnName == $right.SchemaColumn
    | extend Result = case(
        ColumnName == "" and Class == "Mandatory",  strcat ("(0) Error: Missing mandatory field [", SchemaColumn, "]"),
        ColumnName == "" and Class == "Recommended", strcat ("(1) Warning: Missing recommended field [", SchemaColumn, "]"),
        ColumnName == "" and Class == "Conditional" and ParentClass == "Mandatory",
           strcat ("(0) Error: Missing field [", SchemaColumn, "] is mandatory when mandatory column [", AliasedField, "] exists"),
        ColumnName == "" and Class == "Conditional" and AliasedField in (ParserFields),
           strcat ("(0) Error: Missing field [", SchemaColumn, "] is mandatory when field [", AliasedField, "] exists"),  
        ColumnName == "" and Class == "Alias",
            case
              (ParentClass == "Mandatory",
                    iff (AliasedField in (ParserFields),  
                        strcat ("(0) Error: Missing mandatory alias [", SchemaColumn, "] aliasing existing column [", AliasedField, "]"),
                        strcat ("(0) Error: Missing mandatory alias [", SchemaColumn, "] aliasing missing column [", AliasedField, "]")
                    ),
               ParentClass == "Recommended" ,
                    iff (AliasedField in (ParserFields),
                        strcat ("(0) Error: Missing recommended alias [", SchemaColumn, "] aliasing existing column [", AliasedField, "]"),  
                        strcat ("(2) Info: Missing recommended alias [", SchemaColumn, "] aliasing non-existent column [", AliasedField, "]")
                    ),
                // -- default: ParentClass is optional
                iff (AliasedField in (ParserFields),
                    strcat ("(0) Error: Missing optional alias [", SchemaColumn, "] aliasing existing column [", AliasedField, "]"),
                    strcat ("(2) Info: Missing optional alias [", SchemaColumn, "] aliasing non-existent column [", AliasedField, "]")
                )
            ),
        ColumnName == "" and Class == "Optional", strcat ("(2) Info: Missing optional field [", SchemaColumn, "]"),
        SchemaColumn == "", strcat ("(2) Info: extra unnormalized column [", ColumnName, "]"),
        ColumnName != "" and ColumnType != SchemaType, strcat ("(0) Error: type mismatch for column [", ColumnName, "]. It is currently ", ColumnType, " and should be ", SchemaType),
        'None'
        )
    | where Result != "None" | sort by Result asc | project Result
};
```

Run the combined query:

```kql
<ASimSchemaTester function definition above>
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

To run the data validation:
1. Fetch the YAML file at: https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/Testers/ASimDataTester.yaml
2. Parse the YAML content and extract the value under the `ParserQuery` key.
3. Use that extracted KQL as the body of the inline `ASimDataTester` function.

Define the function inline:

```kql
let ASimDataTester = (T:(*),selected_schema:string) {
    <content of the ParserQuery extracted from the YAML file>
};
```

Run the combined query. The `| limit 1000` restricts the number of rows inspected because the data tester evaluates individual row values, which is more expensive than schema-level checks.

```kql
<ASimDataTester function definition above>
<ASIM parser KQL> | limit 1000 | invoke ASimDataTester("<name of the ASIM schema>")
```

### Interpreting data validation results

- **Ignore** errors related to `EventProduct` and `EventVendor` — these are free-form string fields set by the parser author and do not have standard enumerations to validate against.
- **Fix** errors related to enumerated fields — these indicate the parser is producing values that are not in the allowed set for that column.
- **Fix** errors related to data type formatting — these indicate values do not match the expected format (e.g., an IP address column contains non-IP values).

## Outputs
This skill returns the following to the calling skill or orchestrator:
- **Schema validation results** — the list of Error, Warning, and Info messages from `ASimSchemaTester`.
- **Data validation results** — the list of Error, Warning, and Info messages from `ASimDataTester`.
- **Summary** — whether any Error-level `(0)` results remain after both validations.