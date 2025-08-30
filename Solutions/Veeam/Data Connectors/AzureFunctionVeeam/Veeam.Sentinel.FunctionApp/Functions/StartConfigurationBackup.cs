using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Extensions;
using Sentinel.Helpers;
using Sentinel.Managers;

namespace Sentinel.Functions
{
    public class StartConfigurationBackup
    {
        private readonly ILogger<StartConfigurationBackup> _logger;

        private readonly IVbrConnectionsManager _vbrConnectionsManager;
        private readonly ILogAnalyticsManager _logAnalyticsManager;

        public StartConfigurationBackup(ILogger<StartConfigurationBackup> logger, IVbrConnectionsManager vbrConnectionsManager, ILogAnalyticsManager logAnalyticsManager)
        {
            _vbrConnectionsManager = vbrConnectionsManager;
            _logAnalyticsManager = logAnalyticsManager;
            _logger = logger;
        }

        [Function("IngestSessionDataBySessionIdAsync")]
        public async Task<IActionResult> IngestSessionDataBySessionIdAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
        {
            var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);
            var sessionId =RequestParser.GetSessionId(request);
            
            var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

            return await FunctionErrorHandler.ExecuteAsync(
                _logger,
                nameof(IngestSessionDataBySessionIdAsync),
                request.QueryString.ToString(),
                vbrHostName,
                
                async () =>
                {
                    var resp = await client.GetSessionAsync(sessionId);
                    
                    var dto = resp.ToDTO(vbrHostName);
                    
                    // print dto
                    _logger.LogInformation($"Session DTO: {System.Text.Json.JsonSerializer.Serialize(dto)}");

                    await _logAnalyticsManager.SaveSessionDataAsync(dto, vbrHostName);

                    return resp;
                },
                
                resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
            );
        }

        [Function("StartConfigurationBackupAsync")]
        public async Task<IActionResult> StartConfigurationBackupAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
        {
            var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);

            var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

            return await FunctionErrorHandler.ExecuteAsync(
                _logger,
                nameof(StartConfigurationBackupAsync),
                request.QueryString.ToString(),
                vbrHostName,
                
                client.StartConfigurationBackupAsync,
                
                resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
            );
        }
    }
}