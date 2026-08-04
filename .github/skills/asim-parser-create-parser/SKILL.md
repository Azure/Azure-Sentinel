---
name: asim-parser-create-parser
description: This starts the process of creating a new ASIM schema parser by generating the initial version of the parser based on the requirements gathered. Use this skill when you have gathered all necessary information for the new ASIM parser and are ready to create the initial version of the parser.
requiredSkills:
  - log-analytics-workspace-queryer
---

# Prerequisites

Before creating the initial version of a new ASIM parser, ensure you have gathered the following information:

1. The schema of the source data type.
2. The source table name.
3. The target ASIM schema.

## Step 1: Data sampling

Query from the source table to get a sample of the data. Use the `log-analytics-workspace-queryer` skill for all KQL queries in this step.

1. Determine the source table schema with this KQL query: `<tableName> | getschema`. This will give you the column names and data types of the source data, which you can use to map to the ASIM schema.
2. Determine how many rows of data there are with this KQL query: `<tableName> | count`.
3. From the number of rows available in the source table, run this KQL query: `<tableName> | take <minimum of rows found or 2000>`. Take as many rows as possible to get a representative sample. Analyze the rows to identify unique values in important columns that will need to be mapped to the ASIM schema. This will help you understand the transformations needed in the parser.

## Step 2: Build the initial version of the ASIM parser

Use the target ASIM schema to build the ASIM parser.

Determine what fields are **Mandatory**, **Recommended**, or **Optional** using this CSV: https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/ASIM/dev/ASimTester/ASimTester.csv

For details about the different fields, use the Learn Microsoft documentation link to the schema. You do not need to map to every field in the ASIM schema, but you should try to map every column in the source data to an ASIM field.

For more information about developing parsers: https://learn.microsoft.com/en-us/azure/sentinel/normalization-develop-parsers

Do not use existing parsers as a reference. Each parser should be built from the ground up based on the source data and the target ASIM schema. This ensures parsers follow best practices and are optimized for performance.

## Step 3: Parser development guidelines

Parsers are KQL functions that follow a clear flow: **Filter → Parse → Map**.

- Use indexes so only relevant extents are scanned.
- Filter early on native columns before parsing to improve performance.
- Use high-performance parsing operators (`split`, `parse-kv`, `parse`) and avoid regular expressions for string parsing.
- Normalize values with `iff`, `case`, or lookup tables rather than copying source values directly.
- Use `project-rename` for mapping, `extend` for calculated or normalized fields.
- Try to map as many fields as possible, including optional ones. This increases usefulness and future-proofs the parser for schema changes.
- Do not use `project-away` to remove unmapped columns. Use `project` instead, as `project-away` does not protect the parser from schema changes in the source data.

### Parsing operators by performance ranking

| Rank | Operator                   | Description                                                                |
| ---: | -------------------------- | -------------------------------------------------------------------------- |
|    1 | `split`                    | Parse a string of values delimited by a delimiter                          |
|    2 | `parse-kv`                 | Extracts structured information from a string expression in key/value form |
|    3 | `parse_csv`                | Parse a string of values formatted as a CSV line                           |
|    4 | `parse`, `parse-where`     | Parse multiple values from an arbitrary string using a pattern             |
|    5 | `extract_all`              | Parse single values from an arbitrary string using a regular expression    |
|    6 | `extract`                  | Extract a single value from an arbitrary string using a regular expression |
|    7 | `parse_json` (`todynamic`) | Parse values in a string formatted as JSON                                 |
|    8 | `parse_xml`                | Parse the values in a string formatted as XML                              |

### Required columns

- Include the column `Type` in the output of the ASIM parser. This column indicates the source table name.

### Required parameters

Even though this is the parameter-less version, include the following parameters in the KQL function arguments:

- **`disabled: bool = false`** — Allows the parser to be disabled. After calling the table name in the KQL query, include a filter `| where not(disabled)` to ensure the parser can be effectively disabled when needed.

- **`pack: bool = false`** (conditional) — Include this parameter only if the KQL function uses `AdditionalFields`. It allows the user to choose whether to include values in `AdditionalFields` or return it as an empty dynamic. This improves performance for users who do not need the extra information.

## Step 4: Finalize and save

1. **Save** the KQL query in a `.kql` file. The file name must be prefixed with `ASim`, followed by the schema name, event vendor, and event product. For example: `ASimNetworkSessionCiscoASA.kql`. This naming convention is a strict requirement.

2. **Verify** the KQL query runs without syntax errors by using the `log-analytics-workspace-queryer` skill to execute it in the Log Analytics workspace. This step is crucial to validate that the parser is correctly formed and will function as expected when deployed.
