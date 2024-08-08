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
            var alertItem = new AlertItem();
            try
            {
                alertItem.ID = Guid.Parse(row[AlertAttributes.Id]);
                alertItem.Name = row[AlertAttributes.RuleName];
                alertItem.Time = DateTime.Parse(row[AlertAttributes.Time]);
                alertItem.Severity = row[AlertAttributes.RuleSeverityName];
                alertItem.SeverityId = int.Parse(row[AlertAttributes.RuleSeverityId]);
                alertItem.Category = row[AlertAttributes.RuleCategoryName];
                alertItem.Country = MultiValueToStringArray(row[AlertAttributes.LocationCountryName]);
                alertItem.State = MultiValueToStringArray(row[AlertAttributes.LocationSubdivisionName]);
                alertItem.Status = row[AlertAttributes.StatusName];
                alertItem.StatusId = int.Parse(row[AlertAttributes.StatusId]);
                alertItem.CloseReason = row[AlertAttributes.CloseReasonName];
                alertItem.BlacklistLocation = GetBoolValue(row, AlertAttributes.LocationBlacklistedLocation);
                alertItem.AbnormalLocation = MultiValueToStringArray(row[AlertAttributes.LocationAbnormalLocation]);
                alertItem.NumOfAlertedEvents = int.Parse(row[AlertAttributes.EventsCount]);
                alertItem.UserName = MultiValueToStringArray(row[AlertAttributes.UserName]);
                alertItem.SamAccountName = MultiValueToStringArray(row[AlertAttributes.UserSamAccountName]);
                alertItem.PrivilegedAccountType = MultiValueToStringArray(row[AlertAttributes.UserAccountTypeName]);
                alertItem.ContainMaliciousExternalIP = GetBoolValue(row, AlertAttributes.DeviceIsMaliciousExternalIp);
                alertItem.IPThreatTypes = MultiValueToStringArray(row[AlertAttributes.DeviceExternalIpThreatTypesName]);
                alertItem.Asset = MultiValueToStringArray(row[AlertAttributes.AssetPath]);
                alertItem.AssetContainsFlaggedData = MultiValueToBooleanArray(row[AlertAttributes.DataIsFlagged]);
                alertItem.AssetContainsSensitiveData = MultiValueToBooleanArray(row[AlertAttributes.DataIsSensitive]);
                alertItem.Platform = MultiValueToStringArray(row[AlertAttributes.FilerPlatformName]);
                alertItem.FileServerOrDomain = MultiValueToStringArray(row[AlertAttributes.FilerName]);
                alertItem.DeviceName = MultiValueToStringArray(row[AlertAttributes.DeviceHostname]);
                alertItem.IngestTime = DateTime.Parse(row[AlertAttributes.IngestTime]);
                alertItem.EventUTC = GetDateValue(row, AlertAttributes.InitialEventUtcTime);
            }
            catch (Exception ex)
            {
                _logger.LogError("Failed to map search Alert row, skipping alert.", ex);
                return null;
            }

            return alertItem;
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

        private DateTime? GetDateValue(IDictionary<string, string> row, string name)
        {
            return DateTime.TryParse(row[name], out var dateTimeValue) ? (DateTime?)dateTimeValue : null;
        }
    }
}
