# CrowdStrike CCF Data Connectors

## Table of Contents

* [Overview](#overview)
* [Available Data Connectors](#available-data-connectors)

  * [CrowdStrike API Data Connector (via Codeless Connector Framework)](#1-crowdstrike-api-data-connector-via-codeless-connector-framework)
  * [CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)](#2-crowdstrike-falcon-data-replicator-aws-s3-via-codeless-connector-framework)
* [References](#references)

---

## Overview

Microsoft Sentinel provides multiple CrowdStrike data connectors for ingesting security and telemetry data from CrowdStrike Falcon.

This document focuses on the **CrowdStrike Common Connector Framework (CCF)** data connectors and helps customers determine which connector best fits their data ingestion requirements.

The following CrowdStrike CCF data connectors are currently available:

1. **CrowdStrike API Data Connector (via Codeless Connector Framework)**
2. **CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)**

---

## Available Data Connectors

### 1. CrowdStrike API Data Connector (via Codeless Connector Framework)

The **CrowdStrike API Data Connector (via Codeless Connector Framework)** collects data directly from CrowdStrike Falcon native APIs.

Use this connector when you need security-related information that is available through CrowdStrike APIs, including:

* Alerts
* Detections
* Incidents
* Security Findings
* Host Information
* Vulnerability Information
* Other Falcon API-supported datasets

To learn more about the available CrowdStrike APIs and supported datasets, refer to the CrowdStrike API Reference documentation:

**CrowdStrike API Reference**
https://developer.crowdstrike.com/api-reference/overview/

### Configuration Requirements

Before configuring the Microsoft Sentinel connector:

1. Create an API client in CrowdStrike Falcon.
2. Collect the following information:

   * Client ID
   * Client Secret
   * API Endpoint
3. Provide these values during connector configuration in Microsoft Sentinel.

---

### 2. CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)

The **CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)** connector collects telemetry data exported by CrowdStrike to Amazon S3 and ingests it into Microsoft Sentinel.

Use this connector when detailed endpoint telemetry is required, including:

* Process Events
* DNS Events
* Network Events
* Authentication Events
* Endpoint Activity Logs
* Other Falcon Data Replicator (FDR) datasets

These telemetry datasets are generally not available through CrowdStrike native APIs and are delivered through the Falcon Data Replicator (FDR) service.

### Prerequisites

Before configuring the Microsoft Sentinel connector:

1. Create the required AWS resources.
2. Configure an Amazon S3 bucket.
3. Configure an Amazon SQS queue.

AWS setup guidance:

**AWS CrowdStrike Source Setup Documentation**
https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/crowdstrike-source-setup.html

### CrowdStrike Configuration Steps

1. Sign in to CrowdStrike Falcon.
2. Navigate to **Data Sources**.
3. Add a new data source.
4. Select **CrowdStrike Falcon Data Replicator (FDR)**.
5. Provide the required AWS resource information, including:

   * Amazon S3 Bucket
   * Amazon SQS Queue
6. CrowdStrike begins exporting telemetry data to the configured Amazon S3 bucket.

### Microsoft Sentinel Configuration

After telemetry export is configured:

1. Open the **CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)** connector in Microsoft Sentinel.
2. Provide the AWS resource details.
3. Complete the connector deployment.
4. Microsoft Sentinel begins ingesting telemetry data from Amazon S3.

### Data Flow

```text
CrowdStrike Falcon
        ↓
    Amazon S3
        ↓
Microsoft Sentinel
```
                                                    |

### Best Practice

* Use **CrowdStrike API Data Connector (via Codeless Connector Framework)** to collect alerts, detections, incidents, findings, and other data available through CrowdStrike native APIs.
* Use **CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework)** to collect detailed telemetry such as process, DNS, authentication, and network events exported to Amazon S3.
* Deploy **both connectors** when comprehensive visibility across security alerts and endpoint telemetry is required.

---

## References

### CrowdStrike Documentation

* CrowdStrike API Reference
  https://developer.crowdstrike.com/api-reference/overview/

### AWS Documentation

* AWS CrowdStrike Source Setup
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/crowdstrike-source-setup.html
