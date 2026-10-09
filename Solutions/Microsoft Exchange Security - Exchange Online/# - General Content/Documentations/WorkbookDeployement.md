# Deploy Microsoft Exchange Security workbooks

The Microsoft Exchange Security solution packages install workbook templates in Microsoft Sentinel.

## Available workbooks

### Exchange On-Premises

- Microsoft Exchange Admin Activity
- Microsoft Exchange Least Privilege with RBAC
- Microsoft Exchange Search AdminAuditLog
- Microsoft Exchange Security Review

### Exchange Online

- Microsoft Exchange Admin Activity - Online
- Microsoft Exchange Least Privilege with RBAC - Online
- Microsoft Exchange Search AdminAuditLog - Online
- Microsoft Exchange Security Review - Online

## Save a workbook from a template

1. Install or update the required Microsoft Exchange Security solution from **Content Hub**.
2. In Microsoft Sentinel, open **Workbooks**.
3. Open the **Templates** tab.
4. Select the required workbook and open its template.
5. Select **Save**.
6. Choose the subscription, resource group, region, and workbook name.
7. Confirm the save operation, and then open the saved workbook to validate its queries and parameters.

Saving a template creates an independent Azure workbook resource. Changes made to the saved workbook are not overwritten by a solution update, but template improvements delivered by later solution versions are not applied automatically. Review the updated template before manually merging or recreating a customized workbook.

For least-privilege access, see [Delegate access to Microsoft Exchange Security workbooks](./WorkbookDelegation.md).