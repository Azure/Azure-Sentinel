using BeyondTrustPMCloud.Models;
using BeyondTrustPMCloud.Services;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

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
                // Transform data for Log Analytics (add TimeGenerated field and flatten structure)
                var transformedEvents = allEvents.Select(evt => new
                {
                    TimeGenerated = evt.Timestamp,
                    Timestamp = evt.Timestamp,
                    EventId = evt.Event.Id,
                    EventCode = evt.Event.Code,
                    EventKind = evt.Event.Kind,
                    EventCategory = string.Join(",", evt.Event.Category),
                    EventAction = evt.Event.Action,
                    EventOutcome = evt.Event.Outcome,
                    EventType = string.Join(",", evt.Event.Type),
                    EventProvider = evt.Event.Provider,
                    EventIngested = evt.Event.Ingested,
                    EventReason = evt.Event.Reason,
                    EventReceivedAt = evt.Event.ReceivedAt,
                    
                    // Agent information
                    AgentVersion = evt.Agent.Version,
                    AgentId = evt.Agent.Id,
                    AgentEphemeralId = evt.Agent.EphemeralId,
                    
                    // Host information
                    HostHostname = evt.Host.Hostname,
                    HostName = evt.Host.Name,
                    HostId = evt.Host.Id,
                    HostIp = string.Join(",", evt.Host.Ip),
                    HostUptime = evt.Host.Uptime,
                    HostArchitecture = evt.Host.Architecture,
                    HostDomain = evt.Host.Domain,
                    HostDomainIdentifier = evt.Host.DomainIdentifier,
                    HostNetBIOSName = evt.Host.NetBIOSName,
                    HostDomainNetBIOSName = evt.Host.DomainNetBIOSName,
                    HostChassisType = evt.Host.ChassisType,
                    HostOsType = evt.Host.Os.Type,
                    HostOsPlatform = evt.Host.Os.Platform,
                    HostOsName = evt.Host.Os.Name,
                    HostOsFull = evt.Host.Os.Full,
                    HostOsFamily = evt.Host.Os.Family,
                    HostOsVersion = evt.Host.Os.Version,
                    HostOsProductType = evt.Host.Os.ProductType,
                    
                    // User information
                    UserId = evt.User.Id,
                    UserName = evt.User.Name,
                    UserDomain = evt.User.Domain,
                    UserDomainIdentifier = evt.User.DomainIdentifier,
                    UserDomainNetBIOSName = evt.User.DomainNetBIOSName,
                    
                    // File information (if present)
                    FileName = evt.File?.Name,
                    FileAttributes = evt.File != null ? string.Join(",", evt.File.Attributes) : null,
                    FileDirectory = evt.File?.Directory,
                    FileDriveLetter = evt.File?.DriveLetter,
                    FilePath = evt.File?.Path,
                    FileExtension = evt.File?.Extension,
                    FileUid = evt.File?.Uid,
                    FileOwner = evt.File?.OwnerAsString,
                    FileOwnerIdentifier = evt.File?.OwnerAsDetails?.Identifier,
                    FileOwnerDomain = evt.File?.OwnerAsDetails?.DomainName,
                    FileOwnerDomainIdentifier = evt.File?.OwnerAsDetails?.DomainIdentifier,
                    FileOwnerDomainNetBIOSName = evt.File?.OwnerAsDetails?.DomainNetBIOSName,
                    FileCreated = evt.File?.Created,
                    FileDriveType = evt.File?.DriveType,
                    FileProductVersion = evt.File?.ProductVersion,
                    FileHashMd5 = evt.File?.Hash.Md5,
                    FileHashSha1 = evt.File?.Hash.Sha1,
                    FileHashSha256 = evt.File?.Hash.Sha256,
                    
                    // EPM specific information
                    EPMSchemaVersion = evt.EPMWinMac.SchemaVersion,
                    EPMGroupId = evt.EPMWinMac.GroupId,
                    EPMTenantId = evt.EPMWinMac.TenantId,
                    EPMEventAction = evt.EPMWinMac.Event.Action,
                    EPMEventType = evt.EPMWinMac.Event.Type,
                    EPMConfigurationIdentifier = evt.EPMWinMac.Configuration.Identifier,
                    
                    // Related information
                    RelatedIp = string.Join(",", evt.Related.Ip),
                    RelatedUser = string.Join(",", evt.Related.User),
                    RelatedHosts = string.Join(",", evt.Related.Hosts),
                    
                    // ECS information
                    EcsVersion = evt.Ecs.Version,
                    
                    // Tags
                    Tags = string.Join(",", evt.Tags),
                    
                    // Additional properties (as JSON strings for complex objects)
                    ProcessData = evt.Process,
                    NetworkData = evt.Network,
                    DestinationData = evt.Destination,
                    SourceData = evt.Source
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
