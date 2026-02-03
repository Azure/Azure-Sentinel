using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Functions;

public class AuthorizationEvents
{
    private readonly IVbrConnectionsManager _vbrConnectionsManager;
    private readonly ILogAnalyticsManager _logAnalyticsManager;
    private readonly ILogger<AuthorizationEvents> _logger;

    public AuthorizationEvents(IVbrConnectionsManager vbrConnectionsManager, ILogAnalyticsManager logAnalyticsManager, ILogger<AuthorizationEvents> logger)
    {
        _logAnalyticsManager = logAnalyticsManager;
        _vbrConnectionsManager = vbrConnectionsManager;

        _logger = logger;
    }

    [Function("GetAllAuthorizationEventsAsync")]
    public async Task<IActionResult> GetAllAuthorizationEventsAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(GetAllAuthorizationEventsAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                var filter = new AuthorizationEventsFilters();
                var latestDataTime = await _logAnalyticsManager.GetLatestDateTimeIngested(vbrHostName, IngestedStreamType.AuthorizationEvents);

                _logger.LogInformation($"Latest ingested Authorization event time for host {vbrHostName} is {latestDataTime.ToString(LogAnalyticsConstants.DefaultTimeFormat)}");
                
                filter.CreatedAfterFilter = latestDataTime;

                var totalCount = 0;
                filter.Limit = VbrRestApiConstants.DefaultPageSize;
                
                var allEvents = new List<AuthorizationEventsDTO?>();
                
                for (var pageIndex = 0;; pageIndex++)
                {
                    filter.Skip = pageIndex * filter.Limit.Value;

                    var eventsPage = await client.GetAllAuthorizationEventsAsync(filter);

                    if (eventsPage.Data.Count == 0)
                        break;

                    var dtos = eventsPage.Data.Select(me => me.ToDTO(vbrHostName)).ToList();

                    totalCount += dtos.Count;

                    _logger.LogInformation($"Adding page {pageIndex + 1} with {dtos.Count} Authorization events to the list of all events for host {vbrHostName}");

                    allEvents.AddRange(dtos);

                    // If returned less than page size we reached the end
                    if (eventsPage.Data.Count < filter.Limit)
                        break;
                }
                
                await _logAnalyticsManager.SaveAuthorizationEventsToCustomTableAsync(allEvents, vbrHostName);
                
                return $"Ingested total {totalCount} Authorization events for host {vbrHostName}";
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}