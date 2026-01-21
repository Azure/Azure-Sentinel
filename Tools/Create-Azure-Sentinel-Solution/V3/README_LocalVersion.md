# Azure Sentinel Solution Creator V3 - Local Version

## Overview

This is a modified version of the `createSolutionV3.ps1` script that uses the version number from the current solution's data file instead of fetching it from the Microsoft catalog API.

## Files

- **`createSolutionV3_LocalVersion.ps1`** - Modified script that uses local version
- **`createSolutionV3.ps1`** - Original script that uses Microsoft catalog API
- **`README_LocalVersion.md`** - This documentation file

## Key Differences

### Original Script (`createSolutionV3.ps1`)
- Calls `GetCatalogDetails()` to fetch solution details from Microsoft catalog API
- Uses `GetPackageVersion()` to determine version based on catalog data
- May increment version automatically based on published versions
- Requires internet connectivity to Microsoft catalog API

### Modified Script (`createSolutionV3_LocalVersion.ps1`)
- Uses `GetLocalPackageVersion()` function instead of catalog API calls
- Reads version directly from the solution's data file (`Version` field)
- No internet connectivity required for version determination
- No automatic version incrementation based on published versions

## Usage

### Command Line
```powershell
# Run with interactive prompt for path
.\createSolutionV3_LocalVersion.ps1

# Run with specified solution data folder path
.\createSolutionV3_LocalVersion.ps1 -SolutionDataFolderPath "C:\path\to\solution\Data"

# Run with specific version bump type
.\createSolutionV3_LocalVersion.ps1 -SolutionDataFolderPath "C:\path\to\solution\Data" -VersionBump "minor"
```

### Examples
```powershell
# Patch version bump (default): 3.1.8 -> 3.1.9
.\createSolutionV3_LocalVersion.ps1 -SolutionDataFolderPath "C:\Users\fuqingwang\repos\Azure-Sentinel\Solutions\CrowdStrike Falcon Endpoint Protection\Data"

# Minor version bump: 3.1.8 -> 3.2.0
.\createSolutionV3_LocalVersion.ps1 -SolutionDataFolderPath "C:\Users\fuqingwang\repos\Azure-Sentinel\Solutions\CrowdStrike Falcon Endpoint Protection\Data" -VersionBump "minor"

# Major version bump: 3.1.8 -> 4.0.0
.\createSolutionV3_LocalVersion.ps1 -SolutionDataFolderPath "C:\Users\fuqingwang\repos\Azure-Sentinel\Solutions\CrowdStrike Falcon Endpoint Protection\Data" -VersionBump "major"
```