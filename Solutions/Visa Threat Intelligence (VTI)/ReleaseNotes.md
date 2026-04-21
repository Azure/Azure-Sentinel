# Visa Threat Intelligence Plugin for Microsoft Sentinel

## Content

1. Data Connectors – the data connector json files
   * VisaThreatIntelligenceConnector.json
2. Workbooks – workbook json files and black and white preview images of the workbook
   * VTI_IOC_Feed.json
   * Imagaes/Preview/VTIOverview_black.png
   * Imagaes/Preview/VTIOverview_white.png

3. Analytic Rules – yaml file templates of analytic rules
   * VTIP_high_severrity_domain.yaml
   * VTIP_high_severrity_sha1.yaml

### Copyright 2026 Visa Inc.

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|---|---|---|
| 3.0.2 | 04/21/2026 | Updated **createUiDefinition** to include connector information |
| 3.0.1 | 03/10/2026 | Fixed missing data connector information from **mainTemplate** file |
| 3.0.0 | 12/16/2025 | Initial release with **Data Connector**, **Workbook**, and **Analytic Rules** for Visa Threat Intelligence |
