using System;

namespace Varonis.Sentinel.Functions.Search.Model
{
    public static class AlertAttributes
    {
        public const string FilerName = "Alert.Filer.Name";
        public const string Time = "Alert.Time";
        public const string UserIsFlagged = "Alert.User.IsFlagged";
        public const string DataIsSensitive = "Alert.Data.IsSensitive";
        public const string DataIsFlagged = "Alert.Data.IsFlagged";
        public const string CloseReasonName = "Alert.CloseReason.Name";
        public const string LocationSubdivisionName = "Alert.Location.SubdivisionName";
        public const string LocationCountryName = "Alert.Location.CountryName";
        public const string LocationAbnormalLocation = "Alert.Location.AbnormalLocation";
        public const string LocationBlacklistedLocation = "Alert.Location.BlacklistedLocation";
        public const string FilerPlatformName = "Alert.Filer.Platform.Name";
        public const string TimeUTC = "Alert.TimeUTC";
        public const string InitialEventTimeLocal = "Alert.Initial.Event.TimeLocal";
        public const string InitialEventTimeUtc = "Alert.Initial.Event.TimeUTC";
        public const string UserAccountTypeAggregatedName = "Alert.User.AccountType.AggregatedName";
        public const string UserName = "Alert.User.Name";
        public const string UserSamAccountName = "Alert.User.SamAccountName";
        public const string UserAccountTypeName = "Alert.User.AccountType.Name";
        public const string AssignedToVaronis = "Alert.AssignedToVaronis";
        public const string Id = "Alert.ID";
        public const string RuleSeverityName = "Alert.Rule.Severity.Name";
        public const string RuleName = "Alert.Rule.Name";
        public const string DeviceHostName = "Alert.Device.HostName";
        public const string AssetPath = "Alert.Asset.Path";
        public const string StatusName = "Alert.Status.Name";
        public const string ActionTypeName = "Alert.ActionType.Name";
        public const string RuleCategoryName = "Alert.Rule.Category.Name";
        public const string DeviceExternalIpThreatTypesName = "Alert.Device.ExternalIPThreatTypesName";
        public const string DeviceIsMaliciousExternalIp = "Alert.Device.IsMaliciousExternalIP";
        public const string MitreTacticName = "Alert.MitreTactic.Name";
        public const string ClosedByName = "Alert.ClosedByName";
        public const string EventsCount = "Alert.EventsCount";
        public const string IngestTime = "Alert.IngestTime";
        // not publishing to Sentinel
        public const string StatusId = "Alert.Status.ID";
        public const string RuleSeverityId = "Alert.Rule.Severity.ID";
        public const string RuleId = "Alert.Rule.ID";
        public const string SidId = "Alert.User.SidID";

        // not a column
        public const string Aggregate = "Alert.AggregationFilter";

        public static string[] Columns { get; } =
            new string[]
            {
                Id,
                FilerName,
                Time,
                UserIsFlagged,
                DataIsSensitive,
                DataIsFlagged,
                CloseReasonName,
                LocationSubdivisionName,
                LocationCountryName,
                LocationAbnormalLocation,
                LocationBlacklistedLocation,
                FilerPlatformName,
                TimeUTC,
                InitialEventTimeLocal,
                InitialEventTimeUtc,
                UserAccountTypeAggregatedName,
                UserName,
                UserSamAccountName,
                UserAccountTypeName,
                AssignedToVaronis,
                RuleSeverityName,
                RuleName,
                DeviceHostName,
                AssetPath,
                StatusName,
                ActionTypeName,
                RuleCategoryName,
                DeviceExternalIpThreatTypesName,
                DeviceIsMaliciousExternalIp,
                MitreTacticName,
                ClosedByName,
                EventsCount,
                IngestTime,
                // not publishing to Sentinel
                StatusId,
                RuleSeverityId,
                RuleId,
                SidId,
            };
    }
}
