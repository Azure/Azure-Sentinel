# BeyondTrust PM Cloud Workbooks

This folder contains Azure Workbooks for visualizing BeyondTrust Privilege Management Cloud data in Microsoft Sentinel.

## Included Workbooks

### BeyondTrustPMCloud.json - BeyondTrust PM Cloud Overview

This workbook provides comprehensive visibility into BeyondTrust PM Cloud activity and events.

**Features:**
- Event summary tiles showing counts for Activity Audits and Client Events
- Time-based visualizations for both data streams
- Top activity audit actions
- Top client event types
- Top users by activity
- Top hosts by events
- Recent activity audits table
- Recent client events table

**Prerequisites:**
- BeyondTrust PM Cloud data connector must be configured and ingesting data
- Data must be flowing into the following tables:
  - `BeyondTrustPM_ActivityAudits_CL`
  - `BeyondTrustPM_ClientEvents_CL`

**Installation:**
This workbook is automatically deployed when you install the BeyondTrust PM Cloud solution from the Microsoft Sentinel Content Hub.

**Usage:**
1. Navigate to Microsoft Sentinel → Workbooks
2. Find "BeyondTrust PM Cloud" in My Workbooks
3. Click to open and view your data
4. Use the Time Range parameter at the top to adjust the time window

## Customization

You can customize these workbooks after deployment:
1. Open the workbook in Microsoft Sentinel
2. Click "Edit" in the toolbar
3. Modify queries, visualizations, or add new tiles
4. Click "Done Editing" and "Save" to preserve your changes

## Preview Images

Preview images should be black and white PNG files showing the workbook layout. These are displayed in the Microsoft Sentinel Content Hub.
