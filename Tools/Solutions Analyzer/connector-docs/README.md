# Microsoft Sentinel Data Connector Reference

This directory contains comprehensive reference for Microsoft Sentinel data connectors, organized by solutions, connectors, and tables.

## 📑 Documentation Structure

### Index Pages

- **[Solutions Index](solutions-index.md)** - Browse all solutions alphabetically, with overview statistics and quick access to solution details
- **[Connectors Index](connectors-index.md)** - Browse all unique connectors alphabetically, with publisher information, descriptions, and associated tables
- **[Tables Index](tables-index.md)** - Browse all unique tables alphabetically, with solution references, connector counts, transformation support, and ingestion API compatibility

### Solution Pages

Individual solution pages are organized in the [`solutions/`](solutions/) directory. Each solution page includes:

- Solution metadata (title, publisher, description)
- List of data connectors included in the solution
- Detailed connector information (ID, title, description)
- Setup instructions (AI-generated from UI definitions - verify in portal)
- Required permissions and prerequisites
- Tables associated with each connector
- Table uniqueness indicators (whether a table is used by only one connector)

### Connector Pages

Individual connector pages are organized in the [`connectors/`](connectors/) directory. Each connector page includes:

- Connector metadata (ID, publisher)
- Full connector description
- Required permissions and prerequisites
- **Tables Ingested** with transformation and ingestion API support indicators
- **Setup Instructions** - Step-by-step configuration guidance rendered from connector UI definitions using AI
  - ⚠️ **Note**: Instructions are automatically rendered from the user interface definition files using AI and may not be fully accurate. Always verify configuration steps in the Microsoft Sentinel portal.
- Solutions that include this connector
- Links to connector definition files on GitHub

### Table Pages

Individual table pages are organized in the [`tables/`](tables/) directory. Each table page includes:

- Table description from Azure Monitor documentation
- Category and resource types
- Basic Logs eligibility status
- Transformation support status
- Ingestion API compatibility
- Search job support
- Retention information (default and maximum)
- Links to Azure Monitor and Defender XDR documentation
- List of solutions using the table
- List of connectors ingesting data to the table

## 📊 Quick Statistics

For current statistics, see the [Solutions Index](solutions-index.md) which displays up-to-date counts of solutions (with and without connectors), connectors, and tables.

## 🔍 How to Use This Documentation

### Find Information by Solution
Start at the [Solutions Index](solutions-index.md) to browse all available solutions alphabetically. Click on any solution name to view its detailed page with all connectors and tables.

### Find Information by Connector
Use the [Connectors Index](connectors-index.md) to find specific connectors. Each connector entry shows:
- Publisher name
- Full connector description
- Associated solution
- List of tables ingested by the connector

### Find Information by Table
Browse the [Tables Index](tables-index.md) to discover which solutions and connectors use a specific table. The index shows:
- All solutions that include connectors writing to the table
- Number of connectors using the table
- Whether the table supports transformations
- Whether the table supports the Ingestion API

Click on any table name to view its detailed page with Azure Monitor documentation, retention info, and full lists of solutions and connectors.

## 🔄 Navigation

All index pages include a navigation bar at the top for easy switching between different views:

```
Browse by:
- Solutions
- Connectors  
- Tables
```

Solution pages include a back link to return to the Solutions Index.

## 🛠️ Generation

This documentation is automatically generated from the Solutions Analyzer tool, which scans:
- Microsoft Sentinel solution packages
- Data connector definitions
- Parser files and KQL queries

The analyzer identifies table references in connector configurations and parser logic to create comprehensive mappings.

### AI-Generated Instructions

**Setup Instructions** in connector documentation are automatically extracted from connector UI definition files using AI:
- Interprets UI-centric instruction types (DataConnectorsGrid, ContextPane, GCPGrid, AADDataTypes, etc.)
- Converts JSON UI definitions to readable markdown format
- Generates step-by-step configuration guidance
- Describes form fields, dropdowns, and management interfaces
- Marks portal-only features with visual indicators

⚠️ **Important**: AI-generated instructions may not be fully accurate. Always verify all configuration steps in the Microsoft Sentinel portal before implementation.

## 📝 Data Sources

The documentation is based on analysis of:

1. **`solutions_connectors_tables_mapping.csv`** - Contains:
   - Solution metadata
   - Connector configurations
   - Table mappings
   - Detection methods
   - Parser references

2. **`tables_reference.csv`** - Contains:
   - Table metadata from Azure Monitor documentation
   - Basic Logs eligibility
   - Transformation support
   - Ingestion API compatibility
   - Retention information
   - Documentation links

## 🔗 Related Resources

- [Solutions Analyzer Tool](../) - The Python tools that generate this documentation
- [Connector Mapping CSV](../solutions_connectors_tables_mapping.csv) - Connector to table mapping data
- [Tables Reference CSV](../tables_reference.csv) - Table metadata from Azure Monitor documentation
- [Issues Report](../solutions_connectors_tables_issues_and_exceptions_report.csv) - Known issues and exceptions in the analysis

---

*Generated by: Microsoft Sentinel Solutions Analyzer*
