using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Helpers;
using Sentinel.Managers;

namespace Sentinel.Functions;

public class SecurityComplianceAnalyzer
{
    private readonly IVbrConnectionsManager _vbrConnectionsManager;
    private readonly ILogAnalyticsManager _logAnalyticsManager;
    private readonly ILogger<SecurityComplianceAnalyzer> _logger;


    public SecurityComplianceAnalyzer(IVbrConnectionsManager vbrConnectionsManager, ILogAnalyticsManager logAnalyticsManager, ILogger<SecurityComplianceAnalyzer> logger)
    {
        _logAnalyticsManager = logAnalyticsManager;
        _vbrConnectionsManager = vbrConnectionsManager;

        _logger = logger;
    }

    [Function("GetSecurityComplianceAnalyzerResultsAsync")]
    public async Task<IActionResult> GetSecurityComplianceAnalyzerResultsAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        _logger.LogInformation($"Calling {nameof(GetSecurityComplianceAnalyzerResultsAsync)} Azure Function was triggered with query parameters {request.QueryString}");

        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(GetSecurityComplianceAnalyzerResultsAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                var resp = await client.GetSecurityComplianceAnalyzerResultsAsync();

                var dtos = await FilteringHelper.FilterProcessedIdsAsync(resp.Items, vbrHostName, _logAnalyticsManager);

                await _logAnalyticsManager.SaveBestPracticeAnalysisToCustomTableAsync(dtos, vbrHostName);

                return dtos;
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }


    [Function("StartSecurityComplianceAnalyzerAsync")]
    public async Task<IActionResult> StartSecurityComplianceAnalyzerAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        _logger.LogInformation($"Calling {nameof(StartSecurityComplianceAnalyzerAsync)} Azure Function was triggered with query parameters {request.QueryString}");

        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(GetSecurityComplianceAnalyzerResultsAsync),
            request.QueryString.ToString(),
            vbrHostName,

            client.StartSecurityComplianceAnalyzerAsync,

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}