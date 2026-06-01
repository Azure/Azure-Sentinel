using BeyondTrustPMCloud.Models;
using BeyondTrustPMCloud.Services;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace BeyondTrustPMCloud.Functions;

public class ClientEventsFunction
{
    private readonly IBeyondTrustApiService _apiService;
    private readonly ILogAnalyticsService _logAnalyticsService;
    private readonly IStateService _stateService;
    private readonly BeyondTrustConfiguration _config;
    private readonly ILogger<ClientEventsFunction> _logger;

    public ClientEventsFunction(
        IBeyondTrustApiService apiService,
        ILogAnalyticsService logAnalyticsService,
        IStateService stateService,
        BeyondTrustConfiguration config,
        ILogger<ClientEventsFunction> logger)
    {
        _apiService = apiService;
        _logAnalyticsService = logAnalyticsService;
        _stateService = stateService;
        _config = config;
        _logger = logger;
    }

    [Function("ClientEventsTimerTrigger")]
    public async Task Run([TimerTrigger("%ClientEventsCron%")] TimerInfo timer)
    {
        _logger.LogDebug("ClientEvents function started at: {DateTime}", DateTime.Now);

        try
        {
            var state = await _stateService.GetStateAsync(StateKeys.ClientEvents);
            var fromDate = state.LastProcessedTimestamp;

            _logger.LogInformation("Processing Client Events from {FromDate}", fromDate);

            var latestTimestamp = state.LastProcessedTimestamp;
            var lastProcessedEventId = state.LastProcessedEventId;
            var processedAny = false;

            while (true)
            {
                var response = await _apiService.GetClientEventsAsync(fromDate, 1000);

                if (response.Events.Count == 0)
                {
                    _logger.LogDebug("No more Client Events to process");
                    break;
                }

                // Filter against the live in-memory cursor (not the original state snapshot)
                // so that pages 2+ don't re-emit records already sent in this invocation.
                var newEvents = response.Events.Where(e =>
                    e.Event.Ingested > latestTimestamp ||
                    (e.Event.Ingested == latestTimestamp && string.Compare(e.Event.Id, lastProcessedEventId, StringComparison.OrdinalIgnoreCase) > 0)
                ).ToList();

                if (newEvents.Any())
                {
                    var currentLatestTimestamp = newEvents.Max(e => e.Event.Ingested);
                    var currentLatestEventId = newEvents
                        .Where(e => e.Event.Ingested == currentLatestTimestamp)
                        .Max(e => e.Event.Id);

                    if (currentLatestTimestamp > latestTimestamp ||
                        (currentLatestTimestamp == latestTimestamp && string.Compare(currentLatestEventId, lastProcessedEventId, StringComparison.OrdinalIgnoreCase) > 0))
                    {
                        latestTimestamp = currentLatestTimestamp;
                        lastProcessedEventId = currentLatestEventId;
                    }

                    var transformedEvents = TransformClientEvents(newEvents);

                    await _logAnalyticsService.SendToLogAnalyticsAsync(transformedEvents, "BeyondTrustPM_ClientEvents");

                    // Checkpoint after each page so progress survives a host timeout mid-loop.
                    state.LastProcessedTimestamp = DateTime.SpecifyKind(latestTimestamp.AddMilliseconds(1), DateTimeKind.Utc);
                    state.LastProcessedEventId = lastProcessedEventId;
                    state.RecordsProcessed += newEvents.Count;
                    state.Status = "Success";
                    state.ErrorMessage = null;
                    await _stateService.UpdateStateAsync(state);

                    processedAny = true;
                    _logger.LogInformation("✅ Successfully processed {RecordCount} Client Events. Latest Ingested Timestamp: {LatestTimestamp}, Latest Event ID: {LatestEventId}, Next Query From: {NextFromTime}",
                        newEvents.Count, latestTimestamp, lastProcessedEventId, state.LastProcessedTimestamp);

                    if (response.Events.Count < 1000)
                        break;

                    fromDate = currentLatestTimestamp;
                }
                else
                {
                    break;
                }
            }

            if (!processedAny)
            {
                _logger.LogDebug("No new Client Events found");
                state.Status = "Success - No Data";
                state.ErrorMessage = null;
                await _stateService.UpdateStateAsync(state);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error processing Client Events");

            try
            {
                var state = await _stateService.GetStateAsync(StateKeys.ClientEvents);
                state.Status = "Error";
                state.ErrorMessage = ex.Message;
                await _stateService.UpdateStateAsync(state);
            }
            catch (Exception stateEx)
            {
                _logger.LogError(stateEx, "❌ Failed to update error state");
            }

            throw;
        }

        _logger.LogDebug("ClientEvents function completed at: {DateTime}", DateTime.Now);
    }

    private static IEnumerable<object> TransformClientEvents(IEnumerable<ClientEvent> events) =>
        events.Select(evt => (object)new
        {
            // Core timestamp fields
            TimeGenerated = evt.Event.Ingested,
            timestamp = evt.Timestamp,

            // Event fields (10 discrete columns)
            eventId = evt.Event.Id,
            eventCode = evt.Event.Code,
            eventKind = evt.Event.Kind,
            eventCategory = string.Join(",", evt.Event.Category),
            eventAction = evt.Event.Action,
            eventOutcome = evt.Event.Outcome,
            eventType = string.Join(",", evt.Event.Type),
            eventProvider = evt.Event.Provider,
            eventIngested = evt.Event.Ingested,
            eventReason = evt.Event.Reason,

            // Agent fields (2 discrete columns)
            agentVersion = evt.Agent.Version,
            agentId = evt.Agent.Id,

            // Host key fields (8 discrete columns)
            hostHostname = evt.Host.Hostname,
            hostName = evt.Host.Name,
            hostId = evt.Host.Id,
            hostIp = string.Join(",", evt.Host.Ip),
            hostArchitecture = evt.Host.Architecture,
            hostDomain = evt.Host.Domain,
            hostOsType = evt.Host.Os.Type,
            hostOsPlatform = evt.Host.Os.Platform,
            hostOsName = evt.Host.Os.Name,
            hostOsVersion = evt.Host.Os.Version,

            // Host complete data (dynamic column)
            hostData = JsonSerializer.Serialize(evt.Host),

            // User key fields (3 discrete columns)
            userId = evt.User.Id,
            userName = evt.User.Name,
            userDomain = evt.User.Domain,

            // User complete data (dynamic column)
            userData = JsonSerializer.Serialize(evt.User),

            // File key fields (6 discrete columns)
            fileName = evt.File?.Name,
            filePath = evt.File?.Path,
            fileHashMd5 = evt.File?.Hash.Md5,
            fileHashSha1 = evt.File?.Hash.Sha1,
            fileHashSha256 = evt.File?.Hash.Sha256,

            // File complete data (dynamic column)
            fileData = evt.File != null ? JsonSerializer.Serialize(evt.File) : null,

            // Process key fields (3 discrete columns)
            processPid = evt.Process?.Pid,
            processExecutable = evt.Process?.Executable,
            processCommandLine = evt.Process?.CommandLine,

            // Process complete data (dynamic column)
            processData = evt.Process != null ? JsonSerializer.Serialize(evt.Process) : null,

            // EPM key fields (5 discrete columns)
            epmSchemaVersion = evt.EPMWinMac.SchemaVersion,
            epmGroupId = evt.EPMWinMac.GroupId,
            epmTenantId = evt.EPMWinMac.TenantId,
            epmEventAction = evt.EPMWinMac.Event.Action,
            epmEventType = evt.EPMWinMac.Event.Type,

            // EPM complete configuration (dynamic column)
            epmConfigurationData = JsonSerializer.Serialize(evt.EPMWinMac.Configuration),

            // Network complete data (dynamic column)
            networkData = evt.Network != null ? JsonSerializer.Serialize(evt.Network) : null,

            // Destination complete data (dynamic column)
            destinationData = evt.Destination != null ? JsonSerializer.Serialize(evt.Destination) : null,

            // Source complete data (dynamic column)
            sourceData = evt.Source != null ? JsonSerializer.Serialize(evt.Source) : null,

            // Related complete data (dynamic column)
            relatedData = JsonSerializer.Serialize(evt.Related),

            // ECS and tags
            ecsVersion = evt.Ecs.Version,
            tags = string.Join(",", evt.Tags),

            // Transmission timestamp (set at time of sending to Log Analytics)
            timeTransmitted = DateTime.UtcNow
        });
}
