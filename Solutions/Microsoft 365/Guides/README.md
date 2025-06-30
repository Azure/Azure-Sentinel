# Microsoft 365 Solution Guides

This directory contains comprehensive guides for using the Microsoft 365 solution in Microsoft Sentinel.

## Available Guides

### [M365 Copilot Logs Integration Guide](M365-Copilot-Logs.md)
**New!** Learn how to ingest and analyze Microsoft 365 Copilot audit logs using the existing Microsoft 365 data connector. This guide covers:

- Configuration steps for Copilot event ingestion
- Sample KQL queries for monitoring Copilot usage
- Security analytics and threat detection scenarios
- Troubleshooting common issues

### [M365 Copilot FAQ](M365-Copilot-FAQ.md)
**New!** Frequently asked questions about Microsoft 365 Copilot integration with Azure Sentinel, including:

- Do I need a separate data connector?
- What events are available?
- How to verify data ingestion
- Licensing requirements
- Security considerations

**Key Features:**
- ✅ No additional data connector required
- ✅ Uses existing Microsoft 365 connector
- ✅ Comprehensive sample queries
- ✅ Security monitoring templates
- ✅ Workbook integration guidance

## Quick Start

1. **Enable Microsoft 365 Data Connector**: Ensure you have the Microsoft 365 data connector enabled with Exchange, SharePoint, and Teams data types selected.

2. **Verify Copilot Licensing**: Confirm your organization has Microsoft 365 Copilot or E5 licenses.

3. **Test Data Ingestion**: Use the sample queries provided in the guide to verify Copilot events are being ingested.

4. **Deploy Security Rules**: Implement the included hunting queries and analytic rules for monitoring.

## Support

For questions or issues with these guides:
- Review the troubleshooting sections in each guide
- Check the Microsoft 365 data connector status in Sentinel
- Verify audit log retention settings in Microsoft 365 Admin Center
- Contact support through the Azure portal

## Contributing

To contribute to these guides or report issues, please use the Azure Sentinel GitHub repository.