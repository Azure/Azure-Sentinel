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

            var allEvents = new List<ClientEvent>();
            var latestTimestamp = state.LastProcessedTimestamp;
            var lastProcessedEventId = state.LastProcessedEventId;

            // Get events in batches
            while (true)
            {
                var response = await _apiService.GetClientEventsAsync(fromDate, 1000);

                if (response.Events.Count == 0)
                {
                    _logger.LogDebug("No more Client Events to process");
                    break;
                }

                // Filter out already processed events based on event ID and ingested timestamp
                var newEvents = response.Events.Where(e => 
                    e.Event.Ingested > state.LastProcessedTimestamp || 
                    (e.Event.Ingested == state.LastProcessedTimestamp && string.Compare(e.Event.Id, lastProcessedEventId, StringComparison.OrdinalIgnoreCase) > 0)
                ).ToList();

                if (newEvents.Any())
                {
                    allEvents.AddRange(newEvents);

                    // Track the latest ingested timestamp and event ID
                    var currentLatestTimestamp = newEvents.Max(e => e.Event.Ingested);
                    var eventsWithLatestTimestamp = newEvents.Where(e => e.Event.Ingested == currentLatestTimestamp).ToList();
                    var currentLatestEventId = eventsWithLatestTimestamp.Max(e => e.Event.Id);

                    if (currentLatestTimestamp > latestTimestamp || 
                        (currentLatestTimestamp == latestTimestamp && string.Compare(currentLatestEventId, lastProcessedEventId, StringComparison.OrdinalIgnoreCase) > 0))
                    {
                        latestTimestamp = currentLatestTimestamp;
                        lastProcessedEventId = currentLatestEventId;
                    }

                    _logger.LogDebug("Found {NewRecords} new Client Events", newEvents.Count);

                    // If we got fewer events than requested, we've reached the end
                    if (response.Events.Count < 1000)
                    {
                        break;
                    }

                    // Update fromDate for next batch to continue from the latest timestamp
                    fromDate = currentLatestTimestamp;
                }
                else
                {
                    // No new events found, exit loop
                    break;
                }
            }

            if (allEvents.Any())
            {
                // Transform data for Log Analytics using hybrid schema:
                // - Extract 42 key fields to discrete columns for fast querying
                // - Serialize 9 complex structures to dynamic JSON columns for complete data capture
                var transformedEvents = allEvents.Select(evt => new
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
                    eventIngested = evt.Event.Ingested,  // Critical for API filtering
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
                    
                    // Host complete data (dynamic column) - includes all OS details, NetBIOS, chassis, uptime, etc.
                    hostData = JsonSerializer.Serialize(evt.Host),
                    
                    // User key fields (3 discrete columns)
                    userId = evt.User.Id,
                    userName = evt.User.Name,
                    userDomain = evt.User.Domain,
                    
                    // User complete data (dynamic column) - includes domain identifiers, NetBIOS names, etc.
                    userData = JsonSerializer.Serialize(evt.User),
                    
                    // File key fields (6 discrete columns)
                    fileName = evt.File?.Name,
                    filePath = evt.File?.Path,
                    fileHashMd5 = evt.File?.Hash.Md5,
                    fileHashSha1 = evt.File?.Hash.Sha1,
                    fileHashSha256 = evt.File?.Hash.Sha256,
                    
                    // File complete data (dynamic column) - includes pe, code_signature, Owner, bundle, attributes, etc.
                    fileData = evt.File != null ? JsonSerializer.Serialize(evt.File) : null,
                    
                    // Process key fields (3 discrete columns)
                    processPid = evt.Process?.Pid,
                    processExecutable = evt.Process?.Executable,
                    processCommandLine = evt.Process?.CommandLine,
                    
                    // Process complete data (dynamic column) - includes ElevationRequired, user, parent, HostedFile
                    processData = evt.Process != null ? JsonSerializer.Serialize(evt.Process) : null,
                    
                    // EPM key fields (5 discrete columns)
                    epmSchemaVersion = evt.EPMWinMac.SchemaVersion,
                    epmGroupId = evt.EPMWinMac.GroupId,
                    epmTenantId = evt.EPMWinMac.TenantId,
                    epmEventAction = evt.EPMWinMac.Event.Action,
                    epmEventType = evt.EPMWinMac.Event.Type,
                    
                    // EPM complete configuration (dynamic column) - deep nested config structure
                    epmConfigurationData = JsonSerializer.Serialize(evt.EPMWinMac.Configuration),
                    
                    // Network complete data (dynamic column)
                    networkData = evt.Network != null ? JsonSerializer.Serialize(evt.Network) : null,
                    
                    // Destination complete data (dynamic column)
                    destinationData = evt.Destination != null ? JsonSerializer.Serialize(evt.Destination) : null,
                    
                    // Source complete data (dynamic column)
                    sourceData = evt.Source != null ? JsonSerializer.Serialize(evt.Source) : null,
                    
                    // Related complete data (dynamic column) - includes hash, ip, user, hosts arrays
                    relatedData = JsonSerializer.Serialize(evt.Related),
                    
                    // ECS and tags
                    ecsVersion = evt.Ecs.Version,
                    tags = string.Join(",", evt.Tags),
                    
                    // Transmission timestamp (set at time of sending to Log Analytics)
                    timeTransmitted = DateTime.UtcNow
                }).ToList();

                await _logAnalyticsService.SendToLogAnalyticsAsync(transformedEvents, "BeyondTrustPM_ClientEvents");

                // Update state - add 1ms to avoid re-querying the same event
                // Use Event.Ingested timestamp as this is what the API uses for filtering
                // Ensure DateTime is UTC for Azure Table Storage
                state.LastProcessedTimestamp = DateTime.SpecifyKind(latestTimestamp.AddMilliseconds(1), DateTimeKind.Utc);
                state.LastProcessedEventId = lastProcessedEventId;
                state.RecordsProcessed += allEvents.Count;
                state.Status = "Success";
                state.ErrorMessage = null;

                await _stateService.UpdateStateAsync(state);

                _logger.LogInformation("✅ Successfully processed {RecordCount} Client Events. Latest Ingested Timestamp: {LatestTimestamp}, Latest Event ID: {LatestEventId}, Next Query From: {NextFromTime}", 
                    allEvents.Count, latestTimestamp, lastProcessedEventId, state.LastProcessedTimestamp);
            }
            else
            {
                _logger.LogDebug("No new Client Events found");
                
                // Update state with successful run even if no data
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
}
