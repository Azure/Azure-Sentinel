# Utimaco Enterprise Secure Key Manager (ESKM) Solution for Microsoft Sentinel

## Overview

This solution enables integration of Utimaco ESKM (Enterprise Secure Key Manager) logs with Microsoft Sentinel using the Connector Builder (RestApiPoller) platform. It provides:
- Automated ingestion of KMIP server logs
- Prebuilt workbook for monitoring key management and authentication activity
- Analytics rules for threat detection
- Hunting queries for proactive investigation

## Features
- **Data Connector:** Connector Builder (RestApiPoller) poller for ESKM KMIP server logs
- **Workbook:** Visualizes key metrics, event distribution, operation outcomes, authentication trends, and activity timeline
- **Analytics Rules:** Detects brute-force, privilege probing, mass deletion, and authentication anomalies
- **Hunting Queries:** Surfaces rare users, new source IPs, high-volume key retrievals, and after-hours activity

## Deployment
1. Import the solution package into Microsoft Sentinel via Content Hub or ARM template deployment.
2. Configure the data connector with your ESKM API endpoint and credentials.
3. Enable analytic rules and customize thresholds as needed.
4. Use the workbook and hunting queries for monitoring and investigation.

## Support
For support, contact Utimaco:
- Email: support@utimaco.com
- Website: https://utimaco.com/support

## Legal
This solution is provided by Utimaco. See license terms in the solution package or contact support for details.
