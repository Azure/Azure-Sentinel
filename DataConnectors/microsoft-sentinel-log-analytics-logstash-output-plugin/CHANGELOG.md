## 2.3.2
- Fixed silent worker thread death caused by uncaught exceptions in worker processing loop.
- Fixed NullPointerException in SenderWorker when Azure returns a LogsUploadException with a null HTTP response.
- Added resilient error handling with consecutive error tracking to reduce permanent worker failure.

## 2.3.0
- Enabled functionality with logstash 9.4.
- Added optional Id configuration value for telemetry.
- Added DCR stream to sent-batches logging.

## 2.2.2
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
