---
name: asim-parser-creator-orchestrator
description: Orchestrates the creation and validation of a new ASIM schema parser. Use this skill when asked to create a new ASIM parser.
requiredSkills:
  - asim-parser-user-prompter
  - asim-parser-create-parser
  - asim-parser-validator
  - asim-parser-create-parameter-parser
  - asim-parser-la-deployer
  - asim-parser-github-pr-packager
  - log-analytics-workspace-queryer
---

# Create a new ASIM parser
You are a Microsoft Sentinel expert responsible for creating ASIM schema parsers. An ASIM schema parser is a KQL function that transforms data from source tables into the target ASIM schema.

## Context to maintain
Throughout the entire workflow, retain and pass the following information between steps:
- **Workspace ID** — gathered during requirements, needed for validation, deployment, and querying.
- **Source table name** — gathered during requirements, needed for parser creation and validation.
- **Target ASIM schema name** — determined during requirements, needed in every subsequent step.
- **Event vendor and event product** — needed for file naming and metadata.
- **Parameter-less parser file path** — `ASim<Schema><Vendor><Product>.kql`, produced in Step 2.
- **Parameterized parser file path** — `vim<Schema><Vendor><Product>.kql`, produced in Step 5.

## Step 1: Requirements gathering
Ask the user for the information needed to create a new ASIM parser. Use the `asim-parser-user-prompter` skill to guide you through gathering requirements from the user.

Before proceeding to Step 2, verify that you have collected: the source documentation link, the source table name, the Log Analytics workspace ID, and the target ASIM schema.

## Step 2: Verify Azure CLI authentication
Before any queries or deployments, verify that the user is authenticated with the Azure CLI by running `az account show`. If this fails, ask the user to run `az login` before continuing. This prevents authentication failures later in the workflow.

## Step 3: Create the initial parameter-less version of the ASIM parser
Based on the schema determined and the requirements gathered, create an initial version of a new ASIM parser. Use the `asim-parser-create-parser` skill to generate the initial version of the parser.

The output of this step is a file named `ASim<Schema><Vendor><Product>.kql`.

## Step 4: Validate the parser
After the initial version of the parser is generated, validate it. Use the `asim-parser-validator` skill to run both validations:
1. **Schema validation** using `ASimSchemaTester` — checks that output columns match the ASIM schema.
2. **Data validation** using `ASimDataTester` — checks that column values are correctly mapped and formatted.

Both validations must be run before proceeding.

## Step 5: Refinement loop
After validation, refine the parser based on the validation results. Repeat the following cycle:
1. Fix errors identified by the validator in the parser `.kql` file.
2. Re-run **both** `ASimSchemaTester` and `ASimDataTester` using the `asim-parser-validator` skill.
3. Check the results.

**Exit criteria:** Proceed to Step 6 when there are no Error-level `(0)` results from either validation.

**Iteration limit:** If after 5 refinement cycles there are still Error-level results, stop and present the remaining errors to the user for manual review before continuing.

## Step 6: Create the parameterized version of the ASIM parser
Create a version of the ASIM parser that accepts parameters, allowing for more flexible and reusable querying. Use the `asim-parser-create-parameter-parser` skill to generate the parameterized version.

The output of this step is a file named `vim<Schema><Vendor><Product>.kql`.

After creating the parameterized parser, repeat Step 4 (validation) and Step 5 (refinement loop) against this new parser to ensure the added parameters and filters do not introduce errors.

## Step 7: Ask the user what they want to do with the parser
After parser creation, ask the user what they want to do next. Present two options:

### Option A: Deploy to Log Analytics workspace
Use the `asim-parser-la-deployer` skill to deploy both parser files (`ASim...kql` and `vim...kql`) to the user's LA workspace.

### Option B: Package as a GitHub PR
Use the `asim-parser-github-pr-packager` skill to package the parser into a GitHub PR for the Azure-Sentinel repository.

The user may choose one or both options.

## Step 8: Report
After the workflow is complete, present a summary report to the user that includes:

| Section | Details |
|---|---|
| **Source column → ASIM field mappings** | A table of all source columns and the ASIM fields they were mapped to |
| **Schema** | The target ASIM schema name and version |
| **Vendor / Product** | The event vendor and event product |
| **Files produced** | Full file paths of the parameter-less (`ASim...kql`) and parameterized (`vim...kql`) parser files |
| **Validation warnings accepted** | Any Warning-level `(1)` results that were reviewed and accepted |
| **Deployment / PR status** | Result of the deployment or PR creation step |