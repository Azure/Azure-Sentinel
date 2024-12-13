using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.Helpers
{
    internal class SearchAlertObjectMapper : BaseMapper<AlertItem>
    {
        private readonly ILogger _logger;

        public SearchAlertObjectMapper(ILogger logger)
        {
            _logger = logger;
        }

        protected override AlertItem Map(IDictionary<string, string> row)
        {
            try
            {
                var alertItem = new AlertItem
                {
                    AlertId = Guid.Parse(row[AlertAttributes.Id]),
                    ThreatDetectionPolicyName = row[AlertAttributes.RuleName],
                    AlertTime = GetDateValue(row, AlertAttributes.Time),
                    AlertSeverity = row[AlertAttributes.RuleSeverityName],
                    AlertCategory = row[AlertAttributes.RuleCategoryName],
                    Countries = MultiValueToStringArray(row[AlertAttributes.LocationCountryName]),
                    States = MultiValueToStringArray(row[AlertAttributes.LocationSubdivisionName]),
                    Status = row[AlertAttributes.StatusName],
                    CloseReason = row[AlertAttributes.CloseReasonName],
                    BlacklistedLocation = GetBoolValue(row, AlertAttributes.LocationBlacklistedLocation),
                    AbnormalLocations = MultiValueToStringArray(row[AlertAttributes.LocationAbnormalLocation]),
                    EventsCount = GetIntValue(row, AlertAttributes.EventsCount),
                    PrivilegedAccountType = MultiValueToStringArray(row[AlertAttributes.UserAccountTypeName]),
                    UserNames = MultiValueToStringArray(row[AlertAttributes.UserName]),
                    UserSamAccountNames = MultiValueToStringArray(row[AlertAttributes.UserSamAccountName]),
                    ContainsMaliciousExternalIPs = GetBoolValue(row, AlertAttributes.DeviceIsMaliciousExternalIp),
                    AggregatedExternalIPThreatTypes = MultiValueToStringArray(row[AlertAttributes.DeviceExternalIpThreatTypesName]),
                    Assets = MultiValueToStringArray(row[AlertAttributes.AssetPath]),
                    FlaggedDataExposed = MultiValueToBooleanArray(row[AlertAttributes.DataIsFlagged]),
                    SensitiveDataExposed = MultiValueToBooleanArray(row[AlertAttributes.DataIsSensitive]),
                    DataSourceTypes = MultiValueToStringArray(row[AlertAttributes.FilerPlatformName]),
                    DataSources = MultiValueToStringArray(row[AlertAttributes.FilerName]),
                    DeviceNames = MultiValueToStringArray(row[AlertAttributes.DeviceHostName]),
                    InitialEventTimeUTC = GetDateValue(row, AlertAttributes.InitialEventTimeUtc),
                    AccountsHaveFollowUpIndicators = MultiValueToBooleanArray(row[AlertAttributes.UserIsFlagged]),
                    AlertTimeUTC = GetDateValue(row, AlertAttributes.TimeUTC),
                    InitialEventTime = GetDateValue(row, AlertAttributes.InitialEventTimeLocal),
                    AssignedtoVaronis = GetBoolValue(row, AlertAttributes.AssignedToVaronis),
                    EscalationType = row[AlertAttributes.ActionTypeName],
                    MitreTacticName = row[AlertAttributes.MitreTacticName],
                    ClosedBy = row[AlertAttributes.ClosedByName],
                    IngestTime = GetDateValue(row, AlertAttributes.IngestTime),
                };
                return alertItem;
            }
            catch (Exception ex)
            {
                _logger.LogError("Failed to map search Alert row, skipping alert.", ex);
                return null;
            }
        }

        private static string[] MultiValueToStringArray(string multiValue)
        {
            if (string.IsNullOrWhiteSpace(multiValue))
            {
                return null;
            }

            var valuesArray = multiValue.Split(',')
                .Select(v => v.Trim())
                .ToArray();

            return valuesArray;
        }

        private bool?[] MultiValueToBooleanArray(string multiValue)
        {
            if (string.IsNullOrWhiteSpace(multiValue))
            {
                return null;
            }

            var valuesArray = multiValue.Split(',')
                .Select(ConvertToBoolean)
                .ToArray();

            return valuesArray;
        }

        private bool? GetBoolValue(IDictionary<string, string> row, string name)
        {
            return ConvertToBoolean(row[name]);
        }

        private bool? ConvertToBoolean(string boolStr)
        {
            var value = boolStr?.ToLower().Trim();

            if (value == "yes" || value == "1") return true;
            if (value == "no" || value == "0") return false;

            return bool.TryParse(value, out var boolValue) ? (bool?)boolValue : null;
        }

        private static DateTime? GetDateValue(IDictionary<string, string> row, string name)
        {
            return DateTime.TryParse(row[name], out var dateTimeValue) ? dateTimeValue : null;
        }

        private static int? GetIntValue(IDictionary<string, string> row, string name)
        {
            return int.TryParse(row[name], out var intValue) ? intValue : null;
        }
    }
}
