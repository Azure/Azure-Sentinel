---
name: asim-parser-create-parameter-parser
description: This creates the parameterized version of the ASIM schema parser. You should already have the parameter-less version of the parser to help facilitate the parameter parser creation.
requiredSkills:
  - log-analytics-workspace-queryer
---

# Prerequisites
- You have already created the parameter-less version of the ASIM schema parser.
- The target ASIM schema.

## Get the parameters required
You can get the parameters required from accessing the documentation link about the schema. If you do not have the link, find the target ASIM schema from here: https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas

The link should outline what parameters are needed for the parameterized version of the parser.

## Create a new file for the parameterized version of the ASIM parser
The new file name will have the following format:
The file name should be prefixed with vim, followed by the name of the schema, event vendor, and then event product. For example, if you are creating a parser for the ASIM NetworkSession schema for Cisco ASA firewall logs, you could name the file vimNetworkSessionCiscoASA.kql. This is a strict requirement.

Add the contents of the parameter-less version of the parser to the new file.

## Add parameters
From the parameters you have gathered, add it to function arguments for both the function and the function call.

For information about add filters to the parser, look up the documentation here: https://learn.microsoft.com/en-us/azure/sentinel/normalization-develop-parsers#filtering-based-on-parser-parameters

The purpose of the parameters and filters is to improve efficiency of the parser by allowing it to focus on specific data sets and reduce the amount of data that needs to be processed. Filters (or where statements) are added in the beginning of the KQL query.

## Ensure that the KQL query runs without syntax errors
Before finalizing the parser, use the `log-analytics-workspace-queryer` skill to run the KQL query in the Log Analytics workspace to ensure it executes without syntax errors. This step is crucial to validate that the parser is correctly formed and will function as expected when deployed.