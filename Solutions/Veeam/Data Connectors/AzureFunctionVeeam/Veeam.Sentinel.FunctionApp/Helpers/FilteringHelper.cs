using System.Security.Cryptography;
using System.Text;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;
using VoneApiClient.Models;

namespace Sentinel.Helpers
{
    public static class FilteringHelper
    {
        public static async Task<List<BestPracticeAnalysisDTO>> FilterProcessedIdsAsync(
            List<BestPracticesComplianceModel> items,
            string vbrHostName,
            ILogAnalyticsManager _logAnalyticsManager)
        {
            var mapped = items.Select(me => me.ToDTO(vbrHostName)).Where(me => me?.Id != null).ToList();

            var ids = mapped.Select(me => me?.Id).ToList();

            var uniqueIds = await _logAnalyticsManager.FilterProcessedIdsAsync(ids, vbrHostName);

            return mapped.Where(me => uniqueIds.Contains(me.Id.Value)).ToList();
        }

        public static string FormatIdsToString(List<Guid?> ids)
        {
            var parts = ids.Where(me => me != null).Select(me => $"\"{me}\"");
            return string.Join(", ", parts);
        }

        public static List<TriggeredAlarm> FilterAlarmIds(List<TriggeredAlarm> triggeredAlarms)
        {
            var allowedPredefinedAlarmIds = new[] { 314, 315, 331, 332, 342, 344, 364, 365, 370, 391, 403, 316, 378, 369, 376, 377, 381, 395 };

            return triggeredAlarms.Where(alarm => alarm.PredefinedAlarmId.HasValue && allowedPredefinedAlarmIds.Contains(alarm.PredefinedAlarmId.Value)).ToList();
        }
        
        public static string CalculateEventId(string eventType, string eventActivity, string eventTime, string hostname)
        {
            // Replace nulls with empty strings
            eventType = eventType ?? "";
            eventActivity = eventActivity ?? "";
            eventTime = eventTime ?? "";
            hostname = hostname ?? "";
 
            // Concatenate the fields with a separator
            string compositeKey = $"{eventType}|{eventActivity}|{eventTime}|{hostname}";
 
            // Compute SHA256 hash
            using (SHA256 sha256 = SHA256.Create())
            {
                byte[] bytes = Encoding.UTF8.GetBytes(compositeKey);
                byte[] hash = sha256.ComputeHash(bytes);
 
                // Convert hash to hex string
                StringBuilder sb = new StringBuilder();
                foreach (byte b in hash)
                {
                    sb.Append(b.ToString("x2"));
                }
                return sb.ToString();
            }
        }
    }
}