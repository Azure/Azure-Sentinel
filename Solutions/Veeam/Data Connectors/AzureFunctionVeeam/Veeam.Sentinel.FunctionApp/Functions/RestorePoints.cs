using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Helpers;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Functions;

public class RestorePoints
{
    private readonly IVbrConnectionsManager _vbrConnectionsManager;
    private readonly ILogger<RestorePoints> _logger;

    public RestorePoints(IVbrConnectionsManager vbrConnectionsManager, ILogger<RestorePoints> logger)
    {
        _vbrConnectionsManager = vbrConnectionsManager;

        _logger = logger;
    }


    [Function("GetCleanRestorePointsAsync")]
    public async Task<IActionResult> GetCleanRestorePointsAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);
        var vmName = RequestParser.GetVmNameFromQuery(request);
        
        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync<ObjectRestorePointModel?>(
            _logger,
            nameof(GetCleanRestorePointsAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                var filter = new ObjectRestorePointsFilters();
                filter.NameFilter = vmName;
                filter.MalwareStatusFilter = ESuspiciousActivitySeverity.Clean;
                filter.OrderColumn = EObjectRestorePointsFiltersOrderColumn.CreationTime;
                filter.OrderAsc = false;

                var resp = await client.GetAllRestorePointsAsync(filter);

                var list = resp.Data
                    .Where(rp => rp?.MalwareStatus != null)
                    .ToList();

                return list.FirstOrDefault();
            },

            resp =>
            {
                if (resp != null)
                    return Task.FromResult<IActionResult>(new OkObjectResult(resp));

                return Task.FromResult<IActionResult>(new NotFoundObjectResult($"No clean restore points were found in {vbrHostName}."));
            }
        );
    }

    [Function("StartInstantVMRecoveryAsync")]
    public async Task<IActionResult> StartInstantVMRecoveryAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);
        
        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);
        var restorePointId = RequestParser.GetRestorePointId(request);

        return await FunctionErrorHandler.ExecuteAsync<SessionModel?>(
            _logger,
            nameof(GetCleanRestorePointsAsync),
            request.QueryString.ToString(),
            vbrHostName,
         
            async () =>
            {
                var instantViVMRecoverySpec = new InstantViVMRecoverySpec
                {
                    RestorePointId = restorePointId,
                    Type = EInstantVMRecoveryModeType.OriginalLocation,
                    VmTagsRestoreEnabled = true,
                    SecureRestore = new SecureRestoreSpec
                    {
                        AntivirusScanEnabled = true,
                        VirusDetectionAction = EVirusDetectionAction.DisableNetwork,
                        EntireVolumeScanEnabled = true
                    },
                    NicsEnabled = false,
                    PowerUp = true,
                    Reason = "Started Instant Recovery from MS Sentinel Incident"
                };

                return await client.StartInstantVmRecovery(instantViVMRecoverySpec);
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(new { data = resp }))
        );
    }
}