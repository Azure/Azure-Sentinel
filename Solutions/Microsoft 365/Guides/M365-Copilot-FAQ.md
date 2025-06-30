# Microsoft 365 Copilot FAQ

## Frequently Asked Questions

### Q: Do I need a separate data connector for Microsoft 365 Copilot logs?

**A: No, you do not need a separate data connector.** Microsoft 365 Copilot audit events are ingested through the existing **Microsoft 365** data connector in Microsoft Sentinel. Simply ensure you have the Microsoft 365 connector enabled with the appropriate data types (Exchange, SharePoint, Teams) selected.

### Q: What Microsoft 365 Copilot events are available in Sentinel?

**A: The following Copilot events are typically available:**
- User interactions with Copilot across Microsoft 365 applications
- Copilot response generation and delivery
- User queries submitted to Copilot
- Content accessed by Copilot for response generation
- Copilot usage across Teams, Outlook, Word, PowerPoint, Excel, and OneNote

### Q: How can I verify that Copilot events are being ingested?

**A: Use this KQL query to check for Copilot events:**
```kql
OfficeActivity
| where Operation contains "Copilot"
| take 10
```

If this returns no results, verify:
1. Users in your organization have Copilot licenses
2. Copilot features are being actively used
3. Audit logging is enabled in Microsoft 365 Admin Center
4. The Microsoft 365 data connector is properly configured

### Q: What licenses are required for Copilot audit logging?

**A: You need one of the following:**
- Microsoft 365 E5 license
- Copilot for Microsoft 365 license
- Office 365 E5 license

### Q: Can I create custom alerts for Copilot activity?

**A: Yes!** The solution includes pre-built analytic rules and hunting queries for Copilot monitoring. You can also create custom analytic rules using KQL queries targeting the `OfficeActivity` table with operations containing "Copilot".

### Q: How do I monitor Copilot usage for compliance purposes?

**A: Use the provided sample queries to:**
- Track usage patterns by user and department
- Monitor access to sensitive content
- Generate usage reports by workload
- Identify unusual activity patterns

Example compliance query:
```kql
OfficeActivity
| where Operation contains "Copilot"
| summarize CopilotUsage = count() by UserId, OfficeWorkload, bin(TimeGenerated, 1d)
| order by TimeGenerated desc
```

### Q: Are there any specific security considerations for Copilot logs?

**A: Yes, consider monitoring for:**
- Excessive usage that might indicate automation or misuse
- Off-hours activity that could suggest compromised accounts
- Access to sensitive content through Copilot
- Unusual geographic access patterns

The solution includes pre-built security rules for these scenarios.

### Q: Can I integrate Copilot data with existing workbooks?

**A: Absolutely!** You can:
- Modify existing Microsoft 365 workbooks to include Copilot metrics
- Create new workbooks specifically for Copilot analytics
- Use the provided sample queries as building blocks

### Q: What if I don't see any Copilot events in my logs?

**A: This could be due to:**
1. **No Copilot Usage**: Users aren't actively using Copilot features
2. **Licensing Issues**: Verify Copilot licenses are assigned and active
3. **Audit Configuration**: Check that audit logging is enabled in Microsoft 365
4. **Connector Setup**: Ensure the Microsoft 365 connector includes required workloads
5. **Time Delay**: Audit events may take time to appear (up to 24 hours)

### Q: How long are Copilot audit logs retained?

**A: Retention depends on your Microsoft 365 configuration:**
- Default: 90 days in Microsoft 365 audit logs
- E5 customers: Can configure up to 1 year retention
- Sentinel: Based on your Log Analytics workspace retention settings

### Q: Can I export Copilot usage data for reporting?

**A: Yes, you can:**
- Export data directly from Sentinel using KQL queries
- Create scheduled reports using Logic Apps
- Use Power BI integration for advanced reporting
- Export raw data to external systems via APIs

## Additional Resources

- [Complete M365 Copilot Integration Guide](M365-Copilot-Logs.md)
- [Microsoft 365 Data Connector Documentation](https://docs.microsoft.com/azure/sentinel/connect-office-365)
- [Microsoft 365 Audit Log Reference](https://docs.microsoft.com/office/office-365-management-api/office-365-management-activity-api-schema)

## Need Help?

If you have additional questions:
1. Review the comprehensive [M365 Copilot Logs Integration Guide](M365-Copilot-Logs.md)
2. Check the Microsoft 365 data connector status in Sentinel
3. Verify audit log settings in Microsoft 365 Admin Center
4. Contact Azure support through the Azure portal