# Solution Releases

| Date issued | Version Number | Content |
| --- | --- | --- |
| 28/06/23 | 2.0.74 | SAP Audit Control Workbook |
| 18/09/23 | 2.0.76 | SAP Audit Control Workbook <br> Reflect alerts in addition to incidents <br> Added visualizations for better monitoring <br> Focus on SAP alerts by default <br> Exclude users using wildcards- The SAPUsersGetVIP function now supports excluding users using wildcards. For examples, can exclude all firefighters using FF*. <br> The “SAP - Security Audit Log Configuration Change” logic was modified so it will not alert on dummy changes that surface after system restart |
| 01/01/2024 | 3.0.1 | Content migrated to a content hub V3 protocol- to overcome the error of “Creating the resource of type Microsoft.Resources/templateSpecs would exceed the quota of ‘800’ resources of type Microsoft.Resources/templateSpecs per resource group” |
| 02/02/2024 | 3.0.3 | Updated and improved logic for these alert rules: <br> SAP - Execution of an Obsolete or an Insecure Function Module <br> SAP - Multiple Password Changes <br> SAP - Assignment of a sensitive role <br> SAP - Sensitive User's Password Change and Log in <br> SAP - Login from unexpected network <br> SAP - Sensitive privileged user makes a change in another user <br> Updated parsers: <br> SAPChangeDocsLog- support for blank workspaces, added SystemGuid <br> SAPJAVAFilesLogs- switch to SAPControl file-based logs <br> SAPSpoolLog, SAPSpoolOutputLog- handle different SpoolRequestNumber formats in different SAP releases <br> SAPTableDataLog- handle SidGuid, UpdatedOn fields <br> SAPUsersAssignments- inffer user master data changes in near realtime <br> SAPUsersGetPrivileged- allow SAP AS JAVA systems support |
| 06/03/2024 | 3.1.0 | New JAVA AS alert rules <br> SAP - (Preview) AS JAVA - Sensitive Privileged User Signed In <br> SAP - (Preview) AS JAVA - Sign-In from Unexpected Network <br> SAP - (Preview) AS JAVA - User Creates and Uses New User <br> SAP - Execution of an Obsolete or an Insecure Function Module- improved logic |
| 15/04/2024 | 3.1.4 | Bug fixes |
| 25/04/2024 | 3.1.5 | Fixes SAPCONTROL_CL error when using cross workspace feature|

# UI Changes

| Date issued | ETA production | Content |
| --- | --- | --- |
| 23/08/23 | N/A | Multi SID support <br> Edit from UI |

# Agent (latest tag) Releases

| Date issued | Version Number | Content |
| --- | --- | --- |
| 18/10/23 | | excluded feature for swiss-life <br> fix sapcontrol bug |
| 28/09/23 | 80408209 | fix cve issue <br> fix ADR06 issue |
| 11/09/23 | 79434849 | fix different dates chunk - splitting the chunk to 2 parts <br> json keys can be lower case or upper case. |
| 23/07/23 | 76381740 | Multi SID support <br> UI based management <br> Fix SNC bug <br> JAVA support with HTTPs as standalone (no keyvault yet) |
| 18/06/23 | 75036710 | ADR6 optimization <br> Fix related to the db table log handle <br> CR 1/1/23 <br> CR 7.5 202 <br> CR 7.4 201 <br> Roles 271 <br> Initial release of CRs |

# Agent (preview tag) Agent Releases - will move to the latest tag

| Date issued | Version Number | Content |
| --- | --- | --- |
| 14/11/23 | 82841907 | New disrupt feature support lock and unlock user, will use: <br> BAPI_USER_UNLOCK <br> BAPI_USER_LOCK <br> TH_DELETE_USER <br> need to update recommended authorization CR in GitHub <br> Added new table (SAPAgentLog_CL) to reflect agent logs, currently only reflecting Disrupt related logs <br> Deprecated loggingconfig.yaml, need to update documentation <br> Python 3.9 update <br> Moved from Ubuntu to Mariner <br> Updated PyRfc to latest (pyrfc-3.3-cp39-cp39-linux_x86_64) with support to python 3.9 <br> add warning to java instances loop <br> fix turn off sids |
| 06/08/23 | 77679395 | Unilever open bug, sometimes they get timeout in the change doc log selection on Oracle database, I've added an offset of 5 minutes to give the database a chance to Index properly before the selection - this fixed needs to be validated as working with Unilever before pushing it to “latest” tag |
| 16/07/23 | 76381740 | Multi SID support <br> UI based management <br> Fix SNC bug <br> JAVA support with HTTPs as standalone (no keyvault yet) |

# Agent (Disrupt tag) Agent Releases - will move to the review tag

| Date issued | Version Number | Content |
| --- | --- | --- |
| | 81687988 | Deprecated loggingconfig.yaml, need to update documentation |
| | 81636170 | Added new table (SAPAgentLog_CL) to reflect agent logs, currently only reflecting Disrupt related logs <br> Added support for killing user session, this will use TH_DELETE_USER, need to update recommended authorization CR in GitHub |
| | -- | New disrupt feature support lock and unlock user, will use: <br> BAPI_USER_UNLOCK <br> BAPI_USER_LOCK <br> need to update recommended authorization CR in GitHub |