# Release Notes

## 1.1.2 (1/1/2025)
### Changes/Fixes
- Deployment
    - Fixed issue where previous method to deploy Azure Files Share (required for Consumption and Elastic Premium plans) no longer worked and was causing depoyments to fail.
    - Removed key-based authentication between Function App and Storage Account where supported for additional security.
    - Updated Function App PowerShell to version 7.4.
    - Updated post deployment script to use Az module 12.4.
    - Removed hard-coded GUID for Log Analytics role assignment so it doesn't error out in the event of a redeployment.
    - Updated resource provider API versions to latest.

## 1.1.2 (7/9/2024)
### Changes/Fixes
- Function App Code
    - Updated Azure resource ID enrichment logic to pull this informaton directly from the Defender API vs. trying to do a lookup via ARG based on hostname.
    - Updated libraries and PowerShell modules to recent versions.

## 1.1.1 (3/13/2024)
### Changes/Fixes
- Function App Code
    - Fixed bug in calculating full vs. incremental import.
    - Added new fullImport column to MDVMCVEKB and MDVMNISTCVEKB tables to support above bug fix.

## 1.1.0 (2/19/2024)
### Changes/Fixes
- Function App Code
    - Added more efficient PowerShell module to handle sending data to Azure Monitor. Removed unneeded async complexity.
    - Updated .Net libraries to recent versions.
    - Resolved intermittent Azure Monitor HTTP 400 error during high/concurrent loads.
    - Added version.info file to track build version.
    - Removed error action preference of "stop" (code will continue to execute on non-terminating errors).
    - Fixed bug in KB full vs. incremental logic.
- Deployment
    - Updated to included private network option by default and includes non-private network option in the same template.
    - Updated MDVMCVEKB_CL table schema to include the cveSupportability property.
    - Added custom role so Managed Identity only has read access to MDVM tables.
    - Added option to deploy workbooks as part of initial template.
    - Added option to enabled Function App Elastic Premium plan.
    - Removed need for supplying Log Analytics location in addition to resource ID.
    - Added DeploymentVersion configuration property to App Service to track current version.
    - Overall simplification and cleanup.
    - All tables now use the default retention period of the workspace.
    - Switched to Windows App Service plan instead of Linux.

## 1.0.0 (2023)
- Initial Release
