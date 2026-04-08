# Microsoft Sentinel - QRadar Migration Data Collector

**Version: 0.3.2**

## Overview

The QRadar Migration Data Collector extracts custom detection rules and building blocks from IBM QRadar SIEM and converts them into a migration-ready format for Microsoft Sentinel.

## Prerequisites

- **Python 2.7.5+** or **Python 3.6+**
- **QRadar API Token** with Admin privileges. [See QRadar documentation](https://www.ibm.com/docs/en/qradar-common?topic=configuration-creating-authorized-service-token) for more information.
- **curl** (only required when using `--use-curl` on Python 2.7.5–2.7.8)
- **Download the script**: [https://aka.ms/SentinelMigrationScript](https://aka.ms/SentinelMigrationScript)

## Getting Started

1. Create an Authorized Token in the QRadar UI. [See the documenation for more information](https://www.ibm.com/docs/qradar-common?topic=configuration-creating-authorized-service-token).
2. Copy the token for use when running the script
<div style="page-break-before: always;"></div>

## Usage Example

```bash
python3 qradar_collector.py --host 10.1.0.10
```

The script will prompt for your API token securely (input is hidden).

This will create two CSV files:
- `qradar_rules_YYYYMMDDHHMMSS.csv` - Rules with calculated columns
- `qradar_log_sources_YYYYMMDDHHMMSS.csv` - Active log sources (with `--log-sources`)

## Command-Line Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and exit |
| `--host HOST` | QRadar console hostname or IP |
| `--api-version API_VERSION` | QRadar API version (default: latest) |
| `--skip-ssl-verify` | Disable SSL certificate verification for self-signed certificates. See warning below. |
| `--use-curl` | Use curl for HTTP calls (required on Python 2.7.5–2.7.8) |
| `--output-dir OUTPUT_DIR` | Directory for final CSV output files (default: current directory) |
| `--cache-dir PATH` | Path to previously collected data for offline replay (read-only) |
| `--log-sources` | Generate standalone active log sources inventory CSV |
| `--active-days DAYS` | Days of inactivity before a log source is excluded (default: 7) |
| `--debug` | Retain workspace folder and log file on exit |
| `--batch-size SIZE` | Batch size for paginated API calls (default: auto-detected) |

> [!WARNING]
> `--skip-ssl-verify` disables TLS certificate validation. This removes server identity verification and can allow QRadar impersonation, API token interception, and response tampering by a malicious proxy or other on-path attacker. Use only on a trusted management network and trusted QRadar host.

## Running Locally on QRadar Console

Older QRadar appliances typically have Python 2.7.5 installed, which lacks native TLS 1.2 support in the `ssl` module. Use the `--use-curl` flag to work around this limitation. Some QRadar consoles also use self-signed certificates, which is why `--skip-ssl-verify` is shown below:

```bash
python qradar_collector.py --host localhost --use-curl --skip-ssl-verify
```