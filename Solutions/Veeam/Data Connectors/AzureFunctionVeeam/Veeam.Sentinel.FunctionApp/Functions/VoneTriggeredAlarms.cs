using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Sentinel.Managers;

namespace Sentinel.Functions;

public class VoneTriggeredAlarms
{
    private readonly IVoneConnectionsManager _voneConnectionsManager;
    private readonly ILogAnalyticsManager _logAnalyticsManager;
    private readonly ILogger<VoneTriggeredAlarms> _logger;

    public VoneTriggeredAlarms(IVoneConnectionsManager voneConnectionsManager, ILogAnalyticsManager logAnalyticsManager, ILogger<VoneTriggeredAlarms> logger)
    {
        _logAnalyticsManager = logAnalyticsManager;
        _voneConnectionsManager = voneConnectionsManager;
        _logger = logger;
    }

    [Function("GetAllTriggeredAlarmsAsync")]
    public async Task<IActionResult> GetAllTriggeredAlarmsAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var voneHostName = RequestParser.GetVoneHostNameFromQuery(request);

        var client = await _voneConnectionsManager.GetOrCreateAsync(voneHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(GetAllTriggeredAlarmsAsync),
            request.QueryString.ToString(),
            voneHostName,

            async () =>
            {
                var latestDataTime = await _logAnalyticsManager.GetLatestDateTimeIngested(voneHostName, IngestedStreamType.TriggeredAlarms);
                
                var resp = await client.GetTriggeredAlarmsAsync();

                _logger.LogInformation($"Total alarms fetched from VONE: {resp.Count}");
                
                var allowedAlarms = FilteringHelper.FilterAlarmIds(resp);
                
                _logger.LogInformation($"Total alarms after filtering by allowed IDs: {allowedAlarms.Count}");

                var filteredAlarms = allowedAlarms
                    .Where(alarm => alarm.TriggeredTime > latestDataTime)
                    .ToList();

                _logger.LogInformation($"Total alarms after filtering by latest ingested time ({latestDataTime}): {filteredAlarms.Count}");
                
                var dtos = filteredAlarms.Select(alarm => alarm.ToDTO(voneHostName)).ToList();

                await _logAnalyticsManager.SaveTriggeredAlarmsToCustomTableAsync(dtos, voneHostName);

                return dtos;
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }

    [Function("ResolveTriggeredAlarmAsync")]
    public async Task<IActionResult> ResolveTriggeredAlarmAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var voneHostName = RequestParser.GetVoneHostNameFromQuery(request);
        var triggeredAlarmId = RequestParser.ParseTriggeredAlarmId(request);

        var client = await _voneConnectionsManager.GetOrCreateAsync(voneHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(ResolveTriggeredAlarmAsync),
            request.QueryString.ToString(),
            voneHostName,
            
            async () =>
            {
                await client.ResolveTriggeredAlarmAsync(triggeredAlarmId);

                return $"Triggered alarm with triggeredAlarmId {triggeredAlarmId} resolved successfully.";
            },
            
            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}