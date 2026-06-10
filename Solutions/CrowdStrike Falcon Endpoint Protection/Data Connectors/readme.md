# CrowdStrike CCF Data Connectors

## Table of Contents

* Overview
* Available Data Connectors
* References

## Overview

Microsoft Sentinel provides multiple CrowdStrike data connectors. This document focuses on the CrowdStrike Common Connector Framework (CCF) data connectors and helps customers determine which connector best fits their data ingestion requirements.

## Available Data Connectors

The following CrowdStrike CCF data connectors are available:

1. **CrowdStrike Falcon API**
2. **CrowdStrike Falcon Data Replicator (Amazon S3)**

### 1. CrowdStrike Falcon API

The CrowdStrike Falcon API connector collects data directly from CrowdStrike Falcon APIs.

Use this connector when you need security-related data that is available through CrowdStrike native APIs, including:

* Alerts
* Detections
* Incidents
* Security findings
* Other Falcon API-supported data

To learn more about the APIs and data available through CrowdStrike Falcon APIs, refer to the CrowdStrike API Reference documentation:

https://developer.crowdstrike.com/api-reference/overview/

When configuring this connector, create an API client in CrowdStrike Falcon and provide the following information in the Microsoft Sentinel data connector:

* Client ID
* Client Secret
* API Endpoint

This connector is recommended for organizations that primarily require security monitoring, alerting, and incident response data.

### 2. CrowdStrike Falcon Data Replicator (Amazon S3)

The CrowdStrike Falcon Data Replicator (FDR) connector collects telemetry data exported by CrowdStrike to Amazon S3 and ingests it into Microsoft Sentinel.

Use this connector when you need detailed telemetry that is not available through CrowdStrike native APIs, including:

* Process events
* DNS events
* Network events
* Authentication events
* Endpoint activity logs
* Other Falcon Data Replicator (FDR) datasets

Before configuring the Microsoft Sentinel connector, create the required AWS resources, such as the S3 bucket and SQS queue. Guidance for creating the AWS resources can be found here:

https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/crowdstrike-source-setup.html

After the AWS resources are created:

1. In CrowdStrike Falcon, navigate to **Data Sources**.
2. Add a new data source and select **CrowdStrike Falcon Data Replicator (FDR)**.
3. Provide the AWS resource details, including the S3 bucket and SQS queue information.
4. CrowdStrike will begin exporting FDR telemetry to the configured S3 bucket.
5. Configure the Microsoft Sentinel CrowdStrike Falcon Data Replicator (Amazon S3) connector using the AWS resource details.
6. Microsoft Sentinel will ingest the telemetry data from Amazon S3.

Data Flow:

CrowdStrike Falcon → Amazon S3 → Microsoft Sentinel

This connector is recommended for organizations that require detailed endpoint telemetry for advanced threat hunting, investigations, and analytics.


### Note

The two connectors are complementary and can be deployed together.

* Use **CrowdStrike Falcon API** to collect alerts, detections, incidents, and other data available through CrowdStrike native APIs.
* Use **CrowdStrike Falcon Data Replicator (Amazon S3)** to collect detailed telemetry such as process, DNS, and network events exported to Amazon S3.
* Deploy both connectors when comprehensive visibility across security alerts and endpoint telemetry is required.

## References

* CrowdStrike API Reference: https://developer.crowdstrike.com/api-reference/overview/
* AWS CrowdStrike Source Setup: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/crowdstrike-source-setup.html
