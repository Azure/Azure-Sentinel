using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.Monitor.Ingestion;
using BeyondTrustPMCloud.Models;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace BeyondTrustPMCloud.Services;

/// <summary>
/// Service for ingesting logs into Azure Monitor using the Logs Ingestion API.
/// Uses Managed Identity for secure authentication and Data Collection Rules for schema control.
/// </summary>
public interface ILogAnalyticsService
{
    Task SendToLogAnalyticsAsync<T>(IEnumerable<T> data, string logType);
}

/// <summary>
/// Implementation of log ingestion using Azure Monitor Logs Ingestion API.
/// Replaces the deprecated HTTP Data Collector API with modern DCE/DCR-based ingestion.
/// </summary>
public class LogAnalyticsService : ILogAnalyticsService
{
    private readonly LogsIngestionClient _logsIngestionClient;
    private readonly LogAnalyticsConfiguration _config;
    private readonly ILogger<LogAnalyticsService> _logger;

    public LogAnalyticsService(
        LogAnalyticsConfiguration config,
        ILogger<LogAnalyticsService> logger)
    {
        _config = config;
        _logger = logger;

        // Use Managed Identity for authentication (no keys required!)
        var credential = new ManagedIdentityCredential();
        var endpoint = new Uri(_config.DataCollectionEndpoint);
        
        _logsIngestionClient = new LogsIngestionClient(endpoint, credential);
        
        _logger.LogInformation("Initialized LogsIngestionClient with DCE: {Endpoint}", _config.DataCollectionEndpoint);
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
            // Determine which DCR and stream to use based on log type
            var (dcrImmutableId, streamName) = GetDcrAndStreamForLogType(logType);

            // Convert data to BinaryData for ingestion
            var binaryData = BinaryData.FromObjectAsJson(dataList);

            // Send data using Logs Ingestion API
            // Note: UploadAsync expects IEnumerable<BinaryData> where each item is a single log entry
            // For batch upload, we use the entire array as one BinaryData
            var response = await _logsIngestionClient.UploadAsync(
                ruleId: dcrImmutableId,
                streamName: streamName,
                logs: new[] { binaryData },
                cancellationToken: default);

            if (response.IsError)
            {
                _logger.LogError("❌ Failed to send data to Log Analytics. Status: {StatusCode}, Error: {Error}", 
                    response.Status, response.ReasonPhrase);
                throw new RequestFailedException($"Failed to send data to Log Analytics: {response.Status} - {response.ReasonPhrase}");
            }

            _logger.LogInformation("✅ Successfully sent {RecordCount} records to Log Analytics table {LogType} via DCR {DcrId}", 
                dataList.Count, logType, dcrImmutableId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error sending {RecordCount} records to Log Analytics table {LogType}", 
                dataList.Count, logType);
            throw;
        }
    }

    /// <summary>
    /// Maps the log type to the corresponding Data Collection Rule and stream name.
    /// </summary>
    private (string dcrImmutableId, string streamName) GetDcrAndStreamForLogType(string logType)
    {
        return logType.ToLowerInvariant() switch
        {
            "beyondtrustpm_activityaudits" or "beyondtrustpm_activityaudits_cl" => 
                (_config.ActivityAuditsDcrImmutableId, _config.ActivityAuditsStreamName),
            
            "beyondtrustpm_clientevents" or "beyondtrustpm_clientevents_cl" => 
                (_config.ClientEventsDcrImmutableId, _config.ClientEventsStreamName),
            
            _ => throw new ArgumentException($"Unknown log type: {logType}. Expected 'BeyondTrustPM_ActivityAudits' or 'BeyondTrustPM_ClientEvents'.", nameof(logType))
        };
    }
}
