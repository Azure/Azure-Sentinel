# TacitRed Compromised Credentials Solution for Microsoft Sentinel

## Overview

The TacitRed Compromised Credentials solution integrates TacitRed's compromised credential and identity threat intelligence into Microsoft Sentinel using the Codeless Connector Framework (CCF).

## Solution Components

| Component | Description |
|-----------|-------------|
| **Data Connector** | CCF-based REST API poller that ingests compromised credential findings from TacitRed |
| **Custom Table** | `TacitRed_Findings_CL` - stores compromised credential indicators |
| **Analytics Rules** | 2 pre-built detection rules for high-confidence and repeat compromises |
| **Workbook** | SecOps dashboard for visualizing credential compromise trends |

## Prerequisites

- Microsoft Sentinel workspace
- TacitRed API credentials (Client ID and Client Secret)
- Appropriate RBAC permissions to deploy Azure resources

## Deployment

1. Navigate to Microsoft Sentinel Content Hub
2. Search for "TacitRed Compromised Credentials"
3. Click Install and follow the deployment wizard
4. Configure the data connector with your TacitRed API credentials

## Data Schema

The `TacitRed_Findings_CL` table includes:

| Column | Type | Description |
|--------|------|-------------|
| `email_s` | string | Compromised email address |
| `domain_s` | string | Domain of the compromised account |
| `password_s` | string | Partial/hashed password indicator |
| `source_s` | string | Breach source |
| `breach_date_t` | datetime | Date of the breach |
| `confidence_d` | int | Confidence score (0-100) |

## Support

- **Provider**: Data443 Risk Mitigation, Inc.
- **Email**: support@data443.com
- **Website**: https://www.data443.com

## Learn More

- [Microsoft Sentinel Documentation](https://learn.microsoft.com/azure/sentinel/)
- [TacitRed Platform](https://www.data443.com/)
