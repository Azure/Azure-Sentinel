namespace Teams.CustomConnector.Common
{

    /// <summary></summary>
    public static class Constants
    {
        public static string RequestProcessingStarted = "Request processing started.";
        public static string RequestFormatError = "Input request not in correct format";
        public static string RequestDeserialized = "Request deserialization completed.";
        public static string RequestProcessed = "Request processing completed.";
        public static string RequestNotProcessed = "Request could not be processed";

        public static string OMSRequestProcessStarted = "Request to OMS Service started";
        public static string OMSRequestProcessCompleted = "Request to OMS Service completed";
        public static string OMSRequestProcessFailed = "Request to OMS Service failed";

        public static string OMSInitialHttpRequestSent = "HTTP Request to OMS Initial Service Started";
        public static string OMSInitialHttpRequestReceived = "HTTP Request to OMS Initial Service received";
        public static string OMSInitialHttpRequestSuccessful = "HTTP Request to OMS Initial Service successful";
        public static string OMSInitialHttpRequestFailed = "HTTP Request to OMS Initial Service failed";

        public static string OMSDetailHttpRequestSent = "HTTP Request to OMS detail Service started";
        public static string OMSDetailHttpRequestReceived = "HTTP Request to OMS detail Service received";
        public static string OMSDetailHttpRequestSuccessful = "HTTP Request to OMS detail Service successful";
        public static string OMSDetailHttpRequestFailed = "HTTP Request to OMS detail Service failed";

        public static string StorageContainerFound = "Storage container found";
        public static string StorageContainerCreated = "Storage container created";
        public static string StorageContainerCreationFailed = "Storage container creation failed";
        public static string UploadDataToStorageContainerStarted = "Data updload to storage container Started";
        public static string UploadDataToStorageContainerCompleted = "Data upload to storage container completed";
        public static string UploadLogsToStorageContainerStarted = "Logs upload to storage container completed";
        public static string UploadLogsToStorageContainerCompleted = "Logs upload to storage container completed";

        public static string RequestLastExecutionTime = "Fetching last execution time";
        public static string LastExecutionTimeNotFound = "Last execution time not found";
        public static string RequestLastExecutionTimeReceived = "Last execution time received";

        public static string OAuthBearerTokenGenerationStarted = "OAuth Token process started";
        public static string OAuthBearerTokenGenerationCompleted = "OAuth Token process completed";
        public static string OAuthBearerTokenGenerationFailed = "OAuth Token process failed";

        public static string FatalError = "Fatal error , execution aborted";

        public static string AuditLogExtractionStartDateMissing = "Audit extraction date missing in config, Default is set to UTC";

        public static string LogContainerName = "LogContainerName";
        public static string LogFileName = "LogFileName";
        public static string DataContainerName = "DataContainerName";



        public static string StorageContainerName = "log.txt";
        public static string StorageContainerConnectionString = "StorageContainerConnectionString";
        public static string TenantId = "TenantId";
        public static string PublisherGUID = "PublisherGUID";

        public static string ResourceId = "ResourceId";
        public static string ClientId = "ClientId";
        public static string ClientSecret = "ClientSecret";
        public static string AADInstance = "AADInstance";

        public static string AuditLogExtractionStartDate = "AuditLogExtractionStartDate";
        public static string ConnectionIntervalInMinutes = "ConnectionIntervalInMinutes";

        public static string ContentType = "ContentType";

        public static string KeyVaultBaseUrl = "KeyVaultBaseUrl";
        public static string KeyVaultEnabled = "KeyVaultEnabled";

        public static string EnableDirectInjestionToWorkSpace = "EnableDirectInjestionToWorkSpace";
        public static string SentinelCustomerId = "SentinelCustomerId";
        public static string SentinelSharedkey = "SentinelSharedkey";

        public static string EnableArchiving = "EnableArchiving";
    }
}
