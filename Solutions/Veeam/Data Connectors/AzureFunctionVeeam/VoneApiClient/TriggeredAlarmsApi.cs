using System.Net;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using VoneApiClient.Configuration;
using VoneApiClient.Constants;
using VoneApiClient.Exceptions;
using VoneApiClient.Models;

namespace VoneApiClient
{
    public class TriggeredAlarmsApi : ITriggeredAlarmsApi
    {
        public VoneConfiguration _configuration { get; set; }
        private readonly ILogger _logger;

        public TriggeredAlarmsApi(VoneConfiguration configuration, ILogger logger)
        {
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<List<TriggeredAlarm>> GetTriggeredAlarmsAsync(TriggeredAlarmFilter alarmsFilter)
        {
            _logger.LogInformation($"Getting triggered alarms with Offset={alarmsFilter.Offset}, Limit={alarmsFilter.Limit}");

            var detectedAfter = alarmsFilter.DetectedAfterTimeUtcFilter.ToUniversalTime();
            
            // Always include predefinedAlarmId filter
            var filterItems = new List<object>
            {
                new
                {
                    property = "predefinedAlarmId",
                    operation = "in",
                    value = alarmsFilter.PredefinedAlarmIdsFilter
                }
            };

            // Only add triggeredTime filter if detectedAfter is not MinValue
            if (alarmsFilter.DetectedAfterTimeUtcFilter != DateTime.MinValue)
            {
                filterItems.Add(new
                {
                    property = "triggeredTime",
                    operation = "greaterThan",
                    value = detectedAfter.ToString(ApiConstants.DateTimeFormat)
                });
            }

            var combinedFilter = new
            {
                operation = "and",
                items = filterItems.ToArray()
            };

            _logger.LogInformation($"Combined filter: {JsonSerializer.Serialize(combinedFilter)}");
            
            var filterJson = JsonSerializer.Serialize(combinedFilter);
            var encodedFilter = Uri.EscapeDataString(filterJson);

            var url = $"/api/v2.2/alarms/triggeredAlarms?Offset={alarmsFilter.Offset}&Limit={alarmsFilter.Limit}&Filter={encodedFilter}";

            _logger.LogInformation($"Triggered alarms request URL (relative): {url}");

            //_configuration.HttpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "_configuration.AccessToken");

            var response = await _configuration.HttpClient.GetAsync(url);

            if (!response.IsSuccessStatusCode)
            {
                // in case of bad token, the API returns a 401 Unauthorized with empty body
                if (response.StatusCode == HttpStatusCode.Unauthorized)
                    throw new TokenExpiredException();

                throw new Exception($"Failed to get triggered alarms: {response.StatusCode}, response content: {await response.Content.ReadAsStringAsync()}");
            }

            var content = await response.Content.ReadAsStringAsync();

            var resp = JsonSerializer.Deserialize<TriggeredAlarmsResponse>(content, new JsonSerializerOptions() { PropertyNameCaseInsensitive = true });
            _logger.LogInformation($"Deserialized response: Items count = {resp?.Items?.Count ?? 0}");

            return resp?.Items ?? new List<TriggeredAlarm>();
        }

        public async Task ResolveTriggeredAlarmAsync(int predefinedAlaramId)
        {
            _logger.LogInformation($"Resolving triggered alarm with predefinedAlarmId={predefinedAlaramId}");

            var url = "/api/v2.2/alarms/triggeredAlarms/resolve";

            var requestPayload = new
            {
                triggeredAlarmIds = new[] { predefinedAlaramId },
                comment = "Resolved via API from Function App",
                resolveType = "Resolve"
            };

            var jsonContent = JsonSerializer.Serialize(requestPayload);
            _logger.LogInformation($"Request payload for ResolveTriggeredAlarmAsync: {jsonContent}");
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

            var response = await _configuration.HttpClient.PostAsync(url, content);

            if (!response.IsSuccessStatusCode)
            {
                if (response.StatusCode == HttpStatusCode.Unauthorized)
                    throw new TokenExpiredException();

                throw new Exception($"Failed to resolve triggered alarm: {response.StatusCode}, response content: {await response.Content.ReadAsStringAsync()}");
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            _logger.LogInformation($"Raw response body for ResolveTriggeredAlarmAsync: {responseBody}");
            _logger.LogInformation($"Successfully resolved triggered alarm with predefinedAlarmId={predefinedAlaramId}");
        }
    }
}