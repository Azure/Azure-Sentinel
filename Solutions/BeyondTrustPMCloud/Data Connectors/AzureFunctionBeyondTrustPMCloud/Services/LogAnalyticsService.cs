using BeyondTrustPMCloud.Models;
using Microsoft.Extensions.Logging;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace BeyondTrustPMCloud.Services;

public interface ILogAnalyticsService
{
    Task SendToLogAnalyticsAsync<T>(IEnumerable<T> data, string logType);
}

public class LogAnalyticsService : ILogAnalyticsService
{
    private readonly HttpClient _httpClient;
    private readonly LogAnalyticsConfiguration _config;
    private readonly ILogger<LogAnalyticsService> _logger;

    public LogAnalyticsService(
        HttpClient httpClient,
        LogAnalyticsConfiguration config,
        ILogger<LogAnalyticsService> logger)
    {
        _httpClient = httpClient;
        _config = config;
        _logger = logger;
    }

    public async Task SendToLogAnalyticsAsync<T>(IEnumerable<T> data, string logType)
    {
        var dataList = data.ToList();
        if (!dataList.Any())
        {
            _logger.LogDebug("No data to send to Log Analytics for log type {LogType}", logType);
            return;
        }

        _logger.LogInformation("Sending {RecordCount} records to Log Analytics table '{LogType}'", dataList.Count, logType);

        try
        {
            var json = JsonSerializer.Serialize(dataList, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var dateString = DateTime.UtcNow.ToString("r");
            var jsonBytes = Encoding.UTF8.GetBytes(json);
            var contentLength = jsonBytes.Length.ToString();

            var stringToHash = $"POST\n{contentLength}\napplication/json\nx-ms-date:{dateString}\n/api/logs";
            var hashedString = BuildSignature(stringToHash, _config.WorkspaceKey);
            var signature = $"SharedKey {_config.WorkspaceId}:{hashedString}";

            var uri = $"https://{_config.WorkspaceId}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01";

            using var request = new HttpRequestMessage(HttpMethod.Post, uri);
            request.Content = new ByteArrayContent(jsonBytes);
            request.Headers.Add("Authorization", signature);
            request.Headers.Add("Log-Type", logType);
            request.Headers.Add("x-ms-date", dateString);
            request.Headers.Add("time-generated-field", "TimeGenerated");
            request.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");

            var response = await _httpClient.SendAsync(request);

            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("✅ Successfully sent {RecordCount} records to Log Analytics table {LogType}", 
                    dataList.Count, logType);
            }
            else
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("❌ Failed to send data to Log Analytics. Status: {StatusCode}, Response: {Response}", 
                    response.StatusCode, errorContent);
                throw new HttpRequestException($"Failed to send data to Log Analytics: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error sending {RecordCount} records to Log Analytics table {LogType}", 
                dataList.Count, logType);
            throw;
        }
    }

    private static string BuildSignature(string message, string secret)
    {
        var encoding = new ASCIIEncoding();
        var keyByte = Convert.FromBase64String(secret);
        var messageBytes = encoding.GetBytes(message);
        
        using var hmacsha256 = new HMACSHA256(keyByte);
        var hash = hmacsha256.ComputeHash(messageBytes);
        return Convert.ToBase64String(hash);
    }
}
