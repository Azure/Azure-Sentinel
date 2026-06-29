---
name: asim-parser-user-prompter
description: Prompts the user for inputs to create a new ASIM schema parser. Use this skill when you need to gather information from the user to create a new ASIM parser.
---

# ASIM Requirements Gathering

You will need to ask the user for various information before you can create a new ASIM parser. This skill will guide you on what information to ask for and how to ask for it.

## Step 1: Documentation of the source data type

The source data type is the type of data that the ASIM parser will be parsing. Ask the user to provide a **link** to the source's documentation.

## Step 2: Source table name

Ask the user to provide the name of the table where the data type is stored in Microsoft Sentinel.

## Step 3: Log Analytics workspace

Ask the user to provide the Log Analytics workspace ID where the table is stored. This workspace ID is a GUID.

Validate the workspace and table name by querying the workspace using the `log-analytics-workspace-queryer` skill. Provide the skill with the workspace ID and the table name as the query. If the query fails, ask the user to provide the information again.

## Step 4: Evaluate what ASIM schema the source data type maps to

Based on the documentation and the table name, evaluate what ASIM schema the source data type maps to. The available schemas are listed at: https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas. Choose from the schemas there.

If you are not sure which schema it maps to, inform the user that you cannot create a parser without knowing the target ASIM schema.
