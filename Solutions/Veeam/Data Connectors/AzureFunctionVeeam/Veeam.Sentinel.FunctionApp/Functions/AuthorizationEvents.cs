using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
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

                filter.CreatedAfterFilter = latestDataTime;

                var resp = await client.GetAllAuthorizationEventsAsync(filter);

                var dtos = resp.Data.Select(me => me.ToDTO(vbrHostName)).ToList();

                await _logAnalyticsManager.SaveAuthorizationEventsToCustomTableAsync(dtos, vbrHostName);

                return dtos;
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}