using Azure.Data.Tables;
using BeyondTrustPMCloud.Models;
using Microsoft.Extensions.Logging;

namespace BeyondTrustPMCloud.Services;

public interface IStateService
{
    Task<StateEntity> GetStateAsync(string stateKey);
    Task UpdateStateAsync(StateEntity state);
}

public class StateService : IStateService
{
    private readonly TableClient _tableClient;
    private readonly ILogger<StateService> _logger;
    private readonly BeyondTrustConfiguration _config;
    private const string TableName = "BeyondTrustPMCloudState";

    public StateService(TableServiceClient tableServiceClient, BeyondTrustConfiguration config, ILogger<StateService> logger)
    {
        _tableClient = tableServiceClient.GetTableClient(TableName);
        _config = config;
        _logger = logger;
        
        // Ensure table exists
        _tableClient.CreateIfNotExists();
    }

    public async Task<StateEntity> GetStateAsync(string stateKey)
    {
        try
        {
            var response = await _tableClient.GetEntityIfExistsAsync<StateEntity>("BeyondTrustPMCloud", stateKey);
            
            if (response.HasValue)
            {
                _logger.LogDebug("Retrieved state for key {StateKey}: LastProcessed={LastProcessed}", 
                    stateKey, response.Value.LastProcessedTimestamp);
                return response.Value;
            }

            // Return new state entity if not found
            var now = DateTime.UtcNow;
            
            // Parse the historical data timeframe
            var startTimestamp = TimeframeParser.ParseTimeframe(_config.HistoricalDataTimeframe, now, _logger);
            
            var newState = new StateEntity
            {
                RowKey = stateKey,
                LastProcessedTimestamp = DateTime.SpecifyKind(startTimestamp, DateTimeKind.Utc),
                LastProcessedId = 0,
                LastProcessedEventId = string.Empty,
                RecordsProcessed = 0,
                LastRunTimestamp = DateTime.SpecifyKind(now, DateTimeKind.Utc),
                Status = "Initialized"
            };

            _logger.LogInformation("Created new state for key {StateKey} starting from {StartTime}", 
                stateKey, newState.LastProcessedTimestamp);
                
            return newState;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error retrieving state for key {StateKey}", stateKey);
            throw;
        }
    }

    public async Task UpdateStateAsync(StateEntity state)
    {
        try
        {
            // Ensure all DateTime properties are UTC for Azure Table Storage
            state.LastRunTimestamp = DateTime.SpecifyKind(DateTime.UtcNow, DateTimeKind.Utc);
            state.LastProcessedTimestamp = DateTime.SpecifyKind(state.LastProcessedTimestamp, DateTimeKind.Utc);
            
            await _tableClient.UpsertEntityAsync(state);
            
            _logger.LogDebug("Updated state for key {StateKey}: LastProcessed={LastProcessed}, RecordsProcessed={RecordsProcessed}", 
                state.RowKey, state.LastProcessedTimestamp, state.RecordsProcessed);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "❌ Error updating state for key {StateKey}", state.RowKey);
            throw;
        }
    }
}
