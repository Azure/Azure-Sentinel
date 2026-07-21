## 2.4.0
- Worker threads now run as bounded, executor-scheduled passes: recoverable exceptions are logged and the worker resumes on the next cycle; fatal JVM errors are logged and re-thrown.
- Fixed graceful shutdown so in-flight batches are drained (batchers, then unifiers, then senders) before workers stop, bounded by `max_graceful_shutdown_time_seconds`.
- Added configurable upload timeouts `connect_timeout_seconds` (default `15`) and `write_timeout_seconds` (default `60`); connect/write timeouts are retried.
- Added thread id, exception type, batch size, and DCR stream to batch failure logs.

## 2.3.3
- Fixed loss of numeric and boolean type fidelity: fields backed by Logstash's internal JRuby types (e.g. ports, byte counts) are now preserved as native JSON numbers/booleans instead of being converted to strings, ensuring reliable ingestion into DCRs with typed columns.

## 2.3.2
- Fixed silent worker thread death caused by uncaught exceptions in worker processing loop.
- Fixed NullPointerException in SenderWorker when Azure returns a LogsUploadException with a null HTTP response.
- Added resilient error handling with consecutive error tracking to reduce permanent worker failure.
- Added optional Id configuration value for telemetry.
- Added DCR stream to sent-batches logging.

## 2.3.0
- Enabled functionality with logstash 9.4.
- Bumped dependency versions for external libraries (azure-sdk-bom, logback, slf4j, Netty).

## 2.2.1
- Adds info-level logging line when batches are successfully sent.

## 2.2.0
- Adds ability to use either new or old configuration values.

## 2.1.2
- Documentation updates.

## 2.1.1
- Improved efficiency.

## 2.1.0
- Fixed event normalization.

## 2.0.0
- Refactored the plugin from Ruby to Java.
- Added ManagedIdentity authentication.

## 1.x.x (Ruby - deprecated)
The 1.x.x releases are the deprecated Ruby version of this plugin. For the 1.x.x changelog and documentation, see [microsoft-sentinel-log-analytics-logstash-output-plugin](../microsoft-sentinel-log-analytics-logstash-output-plugin/CHANGELOG.md).