namespace Sentinel.Constants
{
    internal static class EnvironmentVariablesConstants
    {
        public const string DceMalwareEventsEndpointLabel = "DCE_MALWARE_EVENTS_INGESTION_ENDPOINT";
        public const string DcrMalwareEventsIdLabel = "DCR_MALWARE_EVENTS_IMMUTABLE_ID";
        public const string MalwareEventsStreamNameLabel = "DCR_MALWARE_EVENTS_STREAM_NAME";

        public const string DceBestPracticeAnalysisEndpointLabel = "DCE_BEST_PRACTICE_ANALYSIS_INGESTION_ENDPOINT";
        public const string DcrBestPracticeAnalysisIdLabel = "DCR_BEST_PRACTICE_ANALYSIS_IMMUTABLE_ID";
        public const string BestPracticeAnalysisStreamNameLabel = "DCR_BEST_PRACTICE_ANALYSIS_STREAM_NAME";

        public const string DceAuthorizationEventsEndpointLabel = "DCE_AUTHORIZATION_EVENTS_INGESTION_ENDPOINT";
        public const string DcrAuthorizationEventsIdLabel = "DCR_AUTHORIZATION_EVENTS_IMMUTABLE_ID";
        public const string AuthorizationEventsStreamNameLabel = "DCR_AUTHORIZATION_EVENTS_STREAM_NAME";

        public const string KeyVaultNameLabel = "KEY_VAULT_NAME";
        public const string WorkspaceIdLabel = "WORKSPACE_ID";
        public const string SubscriptionIdLabel = "SUBSCRIPTION_ID";
        public const string ResourceGroupNameLabel = "RESOURCE_GROUP_NAME";
        public const string WorkspaceNameLabel = "WORKSPACE_NAME";
        public const string VbrWatchlistAliasLabel = "VBR_WATCHLIST_ALIAS";
        public const string VoneWatchlistAliasLabel = "VONE_WATCHLIST_ALIAS";

        public static string DceTriggeredAlarmEndpointLabel = "DCE_TRIGGERED_ALARM_INGESTION_ENDPOINT";
        public static string DcrTriggeredAlarmIdLabel = "DCR_TRIGGERED_ALARM_IMMUTABLE_ID";
        public static string TriggeredAlarmStreamNameLabel = "DCR_TRIGGERED_ALARM_STREAM_NAME";
        
        public static string DceCowareFindingsEndpointLabel = "DCE_COVEWARE_FINDINGS_INGESTION_ENDPOINT";
        public static string DcrCowareFindingsIdLabel = "DCR_COVEWARE_FINDINGS_IMMUTABLE_ID";
        public static string CowareFindingsStreamNameLabel = "DCR_COVEWARE_FINDINGS_STREAM_NAME";
        
        public static string DceSessionDataEndpointLabel = "DCE_SESSION_DATA_INGESTION_ENDPOINT";
        public static string DcrSessionDataIdLabel = "DCR_SESSION_DATA_IMMUTABLE_ID";
        public static string SessionDataStreamNameLabel = "DCR_SESSION_DATA_STREAM_NAME";

        public static string CowareWatchlistAliasLabel = "COVEWARE_WATCHLIST_ALIAS";
        
        public static string CovewareAuthUrlLabel = "COVEWARE_AUTH_URL";
        public static string CovewareEarliestEventTimeLabel = "COVEWARE_EARLIEST_EVENT_TIME";
        public static string CovewareMaxRiskLevelLabel = "COVEWARE_MAX_RISK_LEVEL";
        public static string VeeamEarliestEventLabel = "VEEAM_EARLIEST_EVENT_TIME";

        internal static string CreateKeyVaultUri(string kvName)
        {
            return $"https://{kvName}.vault.azure.net/";
        }
    }
}
