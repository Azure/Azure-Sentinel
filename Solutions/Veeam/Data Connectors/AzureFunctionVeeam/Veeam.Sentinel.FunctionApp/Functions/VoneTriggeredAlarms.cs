using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Sentinel.Managers;
using VoneApiClient.Models;

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

                _logger.LogInformation($"Latest triggered alarm ingestion time for VONE {voneHostName} is {latestDataTime.ToString(LogAnalyticsConstants.DefaultTimeFormat)}");
                
                var totalCount = 0;
                var pageSize = VoneRestApiConstants.DefaultPageSize;
                var allAlarms = new List<TriggeredAlarmDTO>();
                var filter = new TriggeredAlarmFilter();

                filter.DetectedAfterTimeUtcFilter = latestDataTime;
                
                for (var pageIndex = 0;; pageIndex++)
                {
                    var offset = pageIndex * pageSize;

                    filter.Offset = offset;
                    filter.Limit = pageSize;

                    var resp = await client.GetTriggeredAlarmsAsync(filter);

                    if (resp.Count == 0)
                    {
                        _logger.LogInformation($"No more alarms returned from VONE (page {pageIndex + 1}). Stopping pagination.");
                        break;
                    }

                    _logger.LogInformation($"Total alarms fetched from VONE on page {pageIndex + 1}: {resp.Count}");

                    var dtos = resp.Select(alarm => alarm.ToDTO(voneHostName)).ToList();

                    totalCount += dtos.Count;

                    allAlarms.AddRange(dtos);

                    _logger.LogInformation($"Adding page {pageIndex + 1} with {dtos.Count} triggered alarms to the list of all alarms for host {voneHostName}.");

                }

                await _logAnalyticsManager.SaveTriggeredAlarmsToCustomTableAsync(allAlarms, voneHostName);

                _logger.LogInformation($"Finished ingesting triggered alarms for host {voneHostName}. Total ingested: {totalCount}");
                return $"Total {totalCount} alarms ingested for host {voneHostName}";
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