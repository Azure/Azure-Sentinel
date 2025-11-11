using CovewareApiClient.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Sentinel.Managers;

namespace Sentinel.Functions;

public class CowareFindings(ICovewareConnectionsManager covewareConnectionsManager, ILogAnalyticsManager logAnalyticsManager, ILogger<CowareFindings> logger)
{
    [Function("GetAllCovewareFindingsAsync")]
    public async Task<IActionResult> GetAllCovewareFindingsAsync(
        [HttpTrigger(AuthorizationLevel.Function, "get", "post")]
        HttpRequest request)
    {
        var covewareHostName = RequestParser.GetCovewareHostNameFromQuery(request);

        var contentClient = await covewareConnectionsManager.GetOrCreateAsync(covewareHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            logger,
            nameof(GetAllCovewareFindingsAsync),
            request.QueryString.ToString(),
            covewareHostName,
            async () =>
            {
                var latestDataTime = await logAnalyticsManager.GetLatestDateTimeIngested(covewareHostName, IngestedStreamType.CowareFindings);

                var findings = await contentClient.GetCovewareFindingsAsync();

                var dtos = findings.Data.Select(f => f.ToDTO(covewareHostName))
                    .Where(dto => dto.EventTime > latestDataTime)
                    .ToList();
                
                logger.LogInformation($"After filtering, {dtos.Count} new findings remain to be ingested.");

                await logAnalyticsManager.SaveCovewareFindingsToCustomTableAsync(dtos, covewareHostName);

                return dtos;
            },
            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}