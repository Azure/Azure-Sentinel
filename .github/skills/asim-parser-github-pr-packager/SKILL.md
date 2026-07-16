---
name: asim-parser-github-pr-packager
description: Packages the created and validated ASIM schema parser into a GitHub PR for the Azure-Sentinel repository. Use this skill when asked to package a parser into a GitHub PR.
---

# Context

You are responsible for packaging the ASIM parser into a GitHub PR for the Azure-Sentinel repository. This involves creating a PR with the necessary changes to include the new or updated parser in the repository.

## Requirements

You will need the following information to package the parser into a GitHub PR:

- **Parser names** — both the parameter-less parser (`ASim<Schema><Vendor><Product>`) and the parameterized parser (`vim<Schema><Vendor><Product>`)
- **ASIM schema name** that the parser is based on
- **KQL queries** for both parser files
- **Event vendor and event product** - These values can be inferred from the parser names.
- **Source documentation link** provided by the user
- **GitHub repository and branch** to which the PR should be made (defaults to Azure-Sentinel repository, main branch)

## Step 1: Verify prerequisites

Verify the following before proceeding:

1. The Azure-Sentinel repository is cloned locally. If not, ask the user to clone it or provide the local path.
2. The user has a git remote configured with push access. Verify with `git remote -v`.

## Step 2: Create a new branch

Create a new branch based on the target branch (e.g., main) using the naming convention:

```
asim/<schema>-<vendor>-<product>
```

For example: `asim/networksession-cisco-asa`.

## Step 3: Add YAML parser files

Create a YAML file for **each** parser (parameter-less and parameterized) in the directory `Parsers/ASim<SchemaName>/Parsers/`.

For the schema reference in both parser files, use the exact `SchemaTitle` and schema-specific `aka.ms` `SchemaLink` defined for the schema in `.script/tests/asimParsersTest/VerifyASimParserTemplate.py`. Do not substitute a Learn documentation URL.

### Parameter-less parser: `ASim<Schema><Vendor><Product>.yaml`

```yaml
Parser:
  Title: <schema name> ASIM parser for <vendor> <product> <schema name> Events
  Version: '0.1.0'
  LastUpdated: <current date in ISO 8601 format>
Product:
  Name: <vendor> <product>
Normalization:
  Schema: <schema name>
  Version: <schema version>
References:
- Title: ASIM <schema name> Schema
  Link: <schema-specific aka.ms SchemaLink from VerifyASimParserTemplate.py>
- Title: ASIM
  Link: https://aka.ms/AboutASIM
- Title: <vendor> <product> Documentation
  Link: <link to the documentation that the user had provided about the product events>
Description: |
  <description of the parser, including the data source, the use cases that the parser can support, and any other relevant information.>
  This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.
ParserName: ASim<Schema><Vendor><Product>
EquivalentBuiltInParser: _ASim_<SchemaName>_<Vendor><Product>
ParserParams:
  - Name: disabled
    Type: bool
    Default: false
  - Name: pack
    Type: bool
    Default: false
ParserQuery: |
  <KQL query of the parameter-less ASIM parser>
```

### Parameterized parser: `vim<Schema><Vendor><Product>.yaml`

```yaml
Parser:
  Title: <schema name> ASIM filtering parser for <vendor> <product> <schema name> Events
  Version: '0.1.0'
  LastUpdated: <current date in long date format>
Product:
  Name: <vendor> <product>
Normalization:
  Schema: <schema name>
  Version: <schema version>
References:
- Title: ASIM <schema name> Schema
  Link: <schema-specific aka.ms SchemaLink from VerifyASimParserTemplate.py>
- Title: ASIM
  Link: https://aka.ms/AboutASIM
- Title: <vendor> <product> Documentation
  Link: <link to the documentation that the user had provided about the product events>
Description: |
  <description of the filtering parser, including the data source and the additional filter parameters it supports.>
  This parser was created using the agentic ASIM parser creation tool, powered by Skills in GitHub.
ParserName: vim<Schema><Vendor><Product>
EquivalentBuiltInParser: _Im_<SchemaName>_<Vendor><Product>
ParserParams:
  - Name: disabled
    Type: bool
    Default: false
  - Name: pack
    Type: bool
    Default: false
  <additional filter parameters as defined by the schema documentation>
ParserQuery: |
  <KQL query of the parameterized ASIM parser>
```

## Step 4: Add changelog

Create a changelog file in the directory `Parsers/ASim<SchemaName>/CHANGELOG/` for both parser files.

### `<parser name for parameter less parser>.md`

```md
# Changelog for <parser name for parameter less parser>

## Version 0.1.0 - <current date in YYYY-MM-DD format>

- (<current date in YYYY-MM-DD format>) Initial creation of the parser
- <other important mappings done in this version that may be relevant for the user to know>
```

### `<parser name for parameterized parser>.md`

```md
# Changelog for <parser name for parameterized parser>

## Version 0.1.0 - <current date in YYYY-MM-DD format>

- (<current date in YYYY-MM-DD format>) Initial creation of the parser
- <other important mappings done in this version that may be relevant for the user to know>
```

## Step 6: Update unifying parsers

Update the unifying parsers to include the new parsers.

In the directory, `Parsers/ASim<SchemaName>/Parsers/`, there will be two parsers that include all existing parsers (e.g. `ASimAuditEvent.yaml` and `vimAuditEvent.yaml`).
Update the following for both yaml files:

- Parser.Version
- Parser.LastUpdated
- Parsers
  - Add the name of the EquivalentBuiltInParser from the created parser.
- ParserQuery
  - Include the function call, including the correct arguments that are required

## Step 7: Update unify parsers changelog

Update the unifying parsers changelog files.

In the directory, `Parsers/ASim<SchemaName>/CHANGELOG/`, there will be two changelogs regarding the unifying parsers(e.g. `ASimAuditEvent.md` and `vimAuditEvent.md`).
Add a new entry to each changelog file to document the addition of the new parsers.

## Step 8. Check if the table is defined in KQL validation tests

In the directory `.script/tests/KqlvalidationsTests/CustomTables`, check if the source table is defined as one of the files.
If there a file that defines the table, the parser is ready to be used in KQL validation tests in GitHub. You can skip this step.
If there is no file, then we will need to create a file.

```json
{
  "Name": "<source table name>",
  "Properties": [
    { "name": "<property name>", "type": "<column type>" }, ...
  ]
}
```

## Step 9. Generate a sample data file

Extract the EventVendor and EventProduct from the parameter-less parser. Create a sample data file in the directory `Sample Data/ASIM` with the following name:
`{EventVendor}_{EventProduct}_{ASIMSchema}_IngestedLogs.csv`

The headers of the CSV file should match the name of the columns from the source table. The source table columns can be derived from Step 8.
Generate 10 rows of sample data for the CSV file.

- Make sure that you do not use any information that could be used to identify a real person or organization.
- Make sure to use all the columns that exist in the source table.
- For columns that represent enumerations (dictated by the parser), ensure that the values are representative of the possible options from the parser.

## Step 10. Ensure all files are present

For new parsers, ensure that all of the following files are present or have been modified:

- Addition of the new parser files specific to the product being normalized (e.g., `ASimAuditEvent{ProductName}.yaml` and `vimAuditEvent{ProductName}.yaml`)
- Addition of the new changelog files for the new parser files (e.g., `ASimAuditEvent{ProductName}.md` and `vimAuditEvent{ProductName}.md`)
- Modification of the unifying parsers (e.g., `ASimAuditEvent.yaml` and `imAuditEvent.yaml`)
- Modification of the the changelog files for the unifying parsers (e.g., `ASimAuditEvent.md` and `imAuditEvent.md`)
- The sample data file (e.g., `<EventVendor>_<EventProduct>_<ASIMSchema>_IngestedLogs.csv`)

## Step 11. Generate ARM templates

Provided that you are in the root directory of the repository (Azure-Sentinel), run the following command to generate the ARM templates:
`.script\kqlFuncYaml2Arm.ps1`
This will generate the necessary ARM templates for the new parsers and update the unifying parsers.
There should not be any files deleted after running this script.

## Step 11: Commit the changes

Commit all changes with a meaningful commit message, e.g.:

```
Add ASIM <SchemaName> parser for <Vendor> <Product>
```
