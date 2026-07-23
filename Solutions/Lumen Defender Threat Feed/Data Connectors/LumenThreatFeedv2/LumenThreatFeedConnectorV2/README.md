# Lumen Threat Feed Connector V2 - Function Code

## Overview

This Azure Function implements the Lumen Threat Feed Connector V2 for Microsoft Sentinel. It uses a timer-triggered function that retrieves threat intelligence indicators from the Lumen Threat Feed API and uploads them to Microsoft Sentinel.

**Key Features:**

- Timer-triggered function using Azure Functions V2 programming model
- Paginated Lumen API v3 with direct page-by-page processing
- Confidence threshold and indicator type filtering
- Automatic retry with exponential backoff for rate limiting
- Batch uploads to Sentinel TI API (100 indicators per batch)
- 15-minute sync intervals

## File Structure

| File | Purpose |
|------|---------|
| `function_app.py` | Azure Functions V2 entry point with timer trigger decorator |
| `main.py` | Core classes: MSALSetup, SentinelUploader, LumenClientV2 |
| `requirements.txt` | Python dependencies |
| `host.json` | Azure Functions host configuration |
| `__init__.py` | Package initialization |

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `LUMEN_API_KEY` | Lumen API key for authentication |
| `WORKSPACE_ID` | Microsoft Sentinel workspace ID |
| `TENANT_ID` | Azure AD tenant ID |
| `CLIENT_ID` | Azure app registration client ID |
| `CLIENT_SECRET` | Azure app registration client secret |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `LUMEN_BASE_URL` | Lumen API base URL | `https://microsoft-sentinel-api.us1.mss.lumen.com` |
| `LUMEN_CONFIDENCE_THRESHOLD` | Minimum confidence score (0-100) | `65` |
| `LUMEN_ENABLE_IPV4` | Enable IPv4 address indicators | `true` |
| `LUMEN_ENABLE_DOMAIN` | Enable domain name indicators | `true` |
| `LUMEN_POLL_INTERVAL` | Seconds between status polls | `5` |
| `LUMEN_POLL_TIMEOUT` | Max seconds to wait for query completion | `300` |

## Retry Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `DEFAULT_MAX_RETRIES` | 5 | Maximum retry attempts |
| `DEFAULT_BASE_DELAY` | 1.0s | Initial delay between retries |
| `DEFAULT_MAX_DELAY` | 60.0s | Maximum delay cap |
| `CHUNK_SIZE` | 100 | Sentinel API batch limit |
| `POLL_INTERVAL` | 5s | Query status poll interval |
| `POLL_TIMEOUT` | 300s | Query completion timeout |
| `MAX_PAGES` | 1000 | Pagination safeguard limit |

## Troubleshooting

### Deployment Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **403 Forbidden during deployment** | Storage account permissions not propagated | Wait 2-3 minutes and redeploy. The ARM template includes a wait, but RBAC propagation can take longer. |
| **Storage account name already exists** | Storage account names are globally unique | Change the `FunctionName` parameter to use a unique prefix |
| **Invalid App Insights Resource ID** | Incorrect resource ID format | Ensure the full resource path is provided, starting with `/subscriptions/` |

### Runtime Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **403 Forbidden during sync** | Lumen API key invalid or incorrect | Verify your Lumen API key in Function App Configuration > Application Settings |
| **No indicators appearing in Sentinel** | API key invalid or expired | Verify your Lumen API key in Function App Configuration > Application Settings |
| **No indicators appearing in Sentinel** | App registration permissions | Verify the app has **Microsoft Sentinel Contributor** role assigned in the proper Log Analytics Workspace |
| **Function not triggering** | Timer schedule misconfigured | Check the timer trigger schedule in `function_app.py`; verify function is enabled |
| **429 Too Many Requests errors** | Sentinel API rate limiting | This is handled automatically with exponential backoff. If persistent, check logs for details |
| **Query timeout errors** | Lumen API taking too long | Increase `LUMEN_POLL_TIMEOUT` environment variable; contact Lumen support if persistent |
| **Missing environment variables** | Configuration not set | Check Application Settings in Azure portal; all required variables must be set |

Note: The timer trigger runs every 15 minutes by default. For testing, you can manually trigger the function or modify the schedule.
