## Review and Manage Data Table Retention
**Author: Matt Lowe**
**Updated by: Joseph A. Montiel

## Deployment Process
1. Copy the content of the workbook JSON file.
2. Go to the Azure Portal.
3. Go to Microsoft Sentinel.
4. Go to Workbooks.
5. Click 'Add Workbook'.
6. Go into edit mode.
7. Go into the advanced editor.
8. Paste the content that was copied from the JSON file.
9. Click save as and name the workbook 'Archive Log Tool'.

## How to use

### 1. Select scope
1. Set the subscription and workspace to review at the top of the workbook.
2. Choose a tab: **Archive**, **Basic**, or **Auxiliary**.
3. Every bulk dropdown in this workbook lists every table registered in the workspace via the ARM API, regardless of ingestion recency — so tables that rarely receive data still appear.

### 2. Archive tab — interactive and total retention
**Single table:**
1. Click a row in "Tables Found in Workspace" (or "Generated Search Tables" for `_SRCH` tables) to select it.
2. Set **Interactive Retention (days)** and **Total Retention (days)**.
3. Click **Update Retention for {DataType}** (or **Update Retention for {DataType2}** for a search table).

**Bulk update (any number of tables):**
1. Use the **Tables for Bulk Update** dropdown to multi-select tables, or choose **Select All**.
2. Set **Interactive Retention (days)** and **Total Retention (days)** — this value is applied to every selected table.
3. Click each **Send Batch** button that appears, in order. One button appears per 20 tables selected, up to 15 batches (300 tables total).
4. If a table has Azure-enforced immutable retention, that table's request fails on its own — the rest of the tables in the same batch still succeed. Check the JSON response body after each batch for per-request results.

> Archive duration = Total Retention − Interactive Retention. Setting Interactive Retention to **-1** resets a table to the workspace default.

### 3. Basic tab — table plan (Analytics ↔ Basic)
**Single table:**
1. Click a row in the table grid to select it.
2. Choose the **Target Table Plan** (Analytics or Basic).
3. Click **Update Plan to {plan} for {DataType}**.

**Bulk update (any number of tables):**
1. Use the **Tables for Bulk Plan Change** dropdown (or **Select All**).
2. Choose the **Target Table Plan**.
3. Click each **Send Batch** button that appears, in order (20 tables per batch, up to 15 batches / 300 tables).

> A table's plan can only be changed about once per week. Switching Analytics → Basic breaks alerts and summary rules on that table; switching Basic → Analytics restores full features but increases ingestion cost.

### 4. Auxiliary tab — table plan (Auxiliary / Lake)
**Single table:**
1. Click a row in the table grid to select it.
2. Click **Update Plan to Auxiliary for {DataType}**.

**Bulk update (any number of tables):**
1. Use the **Tables for Bulk Auxiliary Change** dropdown (or **Select All**).
2. Click each **Send Batch** button that appears, in order (20 tables per batch, up to 15 batches / 300 tables).

> Not every table supports the Auxiliary plan — unsupported tables fail individually within a batch, and the rest of that batch still succeeds. Alerts stop working on a table once it's switched to Auxiliary, and a table can only change plan about once per week. This tab calls API version **2025-07-01**; the Archive and Basic tabs call **2023-09-01**.

### General bulk-update notes (all tabs)
- Every "Send Batch" button submits one ARM batch request (`/batch?api-version=2020-06-01`) covering up to 20 tables. Click the buttons **in order, one at a time** — a button for Batch 2 only appears once 21+ tables are selected, and so on up to Batch 15 (300 tables).
- A failure for one table inside a batch does not stop the rest of that batch's requests.
- The **Currently selected tables** line above the Send Batch buttons shows exactly which tables the next click will affect.
