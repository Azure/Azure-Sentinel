# WebSocket Data Connector - Configuration Reference

#### Note

This documentation is provided as-is for the WebSocket kind connector, considered preview, as of this writing. The references below should be used as a guide to the expected common behaviors rather than an exhaustive list of documentation on the feature.

<br>

## Request Parameters - WebSocket Specific

The following parameters are specific to WebSocket not covered in the RestApiPoller Request configuration:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `firstWindowBackfillInMin` | `Integer` | `60` | Minutes to backfill on first run when no checkpoint exists. Capped at 60 minutes. Only applies when `startTimeAttributeName` is configured. |

For all other parameters in the `Request` section, refer to the RestApiPoller Codeless Connector Framework (CCF) documentation:
> **📖 [RestApiPoller Data Connector - Request Configuration](https://learn.microsoft.com/en-us/azure/sentinel/data-connector-connection-rules-reference#request-configuration)**

<br>

## Handler Behavior - WebSocket Specific 

### Scheme Enforcement
- Use the websocket protocol `wss://` only. This is required for the parameter `request.apiEndpoint`

### Idle Timeout
| Timeout | Value | Behavior |
|---------|-------|----------|
| Idle timeout | 20 seconds | If no data received, breaks out of receive loop (success, flushes buffered events) |

### Health Status Codes
| Code | Meaning |
|------|---------|
| `WS40001` | Credential validation failures including API key token invalid, expired, or could not be obtained. Retriable if the credential provider indicates a transient issue; non-retriable for permanent authentication failures. |
| `WS40002` | Rule configuration error. The `CollectorConfig` has invalid or missing required fields. For example, malformed JSON path, missing endpoint, unsupported protocol. The rule will not be retried until the configuration is fixed. |
| `WS40005` | Unhandled exception during the message receive/process loop that is unexpected. This includes errors such request not matching WebSocket, other configuration, or timeout categories. This excludes `OperationCanceledException` exception where the cancellation is not reported. |
| `WS40007` | WebSocket window timeout exceeded. The connection remained open longer than the configured `request.timeoutInSeconds` without completing. |
| `WS40009` | Retriable WebSocket connection or processing failure. This includes transient errors such as connection refused, network timeout, DNS resolution failure (< 6 hours), or server-side issues. The message will be retried with backoff. |
| `WS40012` | SSRF protection blocked the connection. The resolved IP address of `request.apiEndpoint` falls within a disallowed range (RFC 1918 private, loopback, link-local, or cloud metadata endpoints). The rule will not be retried until the endpoint is changed to an allowed address. |
| `WS50020` | Remote API returned a failure status in the response payload. The WebSocket message was received and parsed, but the response body contains a status field indicating the request was not successful (checked via `response.successStatusJsonPath`). |

