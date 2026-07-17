using CovewareApiClient.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.DTOs;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Sentinel.Managers;

namespace Sentinel.Functions;

public class CovewareFindings(ICovewareConnectionsManager covewareConnectionsManager, ILogAnalyticsManager logAnalyticsManager, ILogger<CovewareFindings> logger)
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
                var latestDataTime = await logAnalyticsManager.GetLatestDateTimeIngested(covewareHostName, IngestedStreamType.CovewareFindings);

                logger.LogInformation($"Latest Coveware finding ingestion time for host {covewareHostName} is {latestDataTime.ToString(LogAnalyticsConstants.DefaultTimeFormat)}");
                
                var totalCount = 0;
                var pageSize = CovewareWatchlistConstants.DefaultPageSize;

                var allFindings = new List<CovewareFindingDTO>();

                for (var pageIndex = 0;; pageIndex++)
                {
                    var filter = new CovewareFindingFilter
                    {
                        DetectedAfterTimeUtcFilter = latestDataTime,
                        Offset = (pageIndex * pageSize).ToString(),
                        PageSize = pageSize.ToString()
                    };

                    var findingsPage = await contentClient.GetCovewareFindingsAsync(filter);

                    if (findingsPage?.Data == null || findingsPage.Data.Count == 0)
                        break;

                    var dtos = findingsPage.Data.Where(f => f.EventTime > latestDataTime)
                        .Select(f =>
                            f.ToDTO(covewareHostName, FilteringHelper.CalculateEventId(
                                f.EventType,
                                f.EventActivity,
                                f.EventTime.ToLongTimeString(),
                                f.Hostname)))
                        .ToList();

                    allFindings.AddRange(dtos);

                    totalCount += dtos.Count;

                    logger.LogInformation($"Adding page {pageIndex} with {dtos.Count} Coveware findings to the list for host {covewareHostName}");

                    // If returned less than page size we reached the end
                    if (findingsPage.Data.Count < pageSize)
                        break;
                }

                logger.LogInformation($"Total events from all pages {totalCount}");

                // For each EventId, select the finding with the most recent ScanTime
                var distinctFindings = allFindings
                    .GroupBy(f => f.EventId)
                    .Select(g => g.OrderByDescending(f => f.ScanTime).First())
                    .ToList();

                await logAnalyticsManager.SaveCovewareFindingsToCustomTableAsync(distinctFindings, covewareHostName);

                return $"Ingested total {distinctFindings.Count} Coveware findings for host {covewareHostName}";
            },
            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}