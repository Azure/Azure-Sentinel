namespace Varonis.Sentinel.Functions.Search.Model
{
    public static class AlertAttributes
    {
        public const string Id = "Alert.ID";
        public const string RuleName = "Alert.Rule.Name";
        public const string RuleId = "Alert.Rule.ID";
        public const string Time = "Alert.TimeUTC";
        public const string RuleSeverityName = "Alert.Rule.Severity.Name";
        public const string RuleSeverityId = "Alert.Rule.Severity.ID";
        public const string RuleCategoryName = "Alert.Rule.Category.Name";
        public const string LocationCountryName = "Alert.Location.CountryName";
        public const string LocationSubdivisionName = "Alert.Location.SubdivisionName";
        public const string StatusName = "Alert.Status.Name";
        public const string StatusId = "Alert.Status.ID";
        public const string EventsCount = "Alert.EventsCount";
        public const string InitialEventUtcTime = "Alert.Initial.Event.TimeUTC";
        public const string UserName = "Alert.User.Name";
        public const string UserSamAccountName = "Alert.User.SamAccountName";
        public const string UserAccountTypeName = "Alert.User.AccountType.Name";
        public const string DeviceHostname = "Alert.Device.HostName";
        public const string DeviceIsMaliciousExternalIp = "Alert.Device.IsMaliciousExternalIP";
        public const string DeviceExternalIpThreatTypesName = "Alert.Device.ExternalIPThreatTypesName";
        public const string DataIsFlagged = "Alert.Data.IsFlagged";
        public const string DataIsSensitive = "Alert.Data.IsSensitive";
        public const string FilerPlatformName = "Alert.Filer.Platform.Name";
        public const string AssetPath = "Alert.Asset.Path";
        public const string FilerName = "Alert.Filer.Name";
        public const string CloseReasonName = "Alert.CloseReason.Name";
        public const string LocationBlacklistedLocation = "Alert.Location.BlacklistedLocation";
        public const string LocationAbnormalLocation = "Alert.Location.AbnormalLocation";
        public const string SidId = "Alert.User.SidID";
        public const string Aggregate = "Alert.AggregationFilter";
        public const string IngestTime = "Alert.IngestTime";

        public static string[] Columns { get; } =
            new string[]
            {
                    Id,
                    RuleName,
                    RuleId,
                    Time,
                    RuleSeverityName,
                    RuleSeverityId,
                    RuleCategoryName,
                    LocationCountryName,
                    LocationSubdivisionName,
                    StatusName,
                    StatusId,
                    EventsCount,
                    InitialEventUtcTime,
                    UserName,
                    UserSamAccountName,
                    UserAccountTypeName,
                    DeviceHostname,
                    DeviceIsMaliciousExternalIp,
                    DeviceExternalIpThreatTypesName,
                    DataIsFlagged,
                    DataIsSensitive,
                    FilerPlatformName,
                    AssetPath,
                    FilerName,
                    CloseReasonName,
                    LocationBlacklistedLocation,
                    LocationAbnormalLocation,
                    SidId,
                    IngestTime
            };
    }
}
