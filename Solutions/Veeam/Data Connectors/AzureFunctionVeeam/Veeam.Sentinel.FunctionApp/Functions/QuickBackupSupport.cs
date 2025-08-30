using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.DTOs;
using Sentinel.Helpers;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;
using Enum = System.Enum;

namespace Sentinel.Functions;

public class QuickBackupSupport
{
    private readonly ILogger<QuickBackupSupport> _logger;
    private readonly IVbrConnectionsManager _vbrConnectionsManager;

    public QuickBackupSupport(IVbrConnectionsManager vbrConnectionsManager, ILogger<QuickBackupSupport> logger)
    {
        _vbrConnectionsManager = vbrConnectionsManager;

        _logger = logger;
    }

    [Function("StartQuickBackupJobAsync")]
    public async Task<IActionResult> StartQuickBackupJobAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        _logger.LogInformation($"Calling {nameof(StartQuickBackupJobAsync)} Azure Function was triggered with query parameters {request.QueryString}");
        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);

        var vmHostName = RequestParser.GetVmHostNameFromQuery(request);
        var vmName = RequestParser.GetVmNameFromQuery(request);
        var viType = RequestParser.GetViTypeFromQuery(request);
        var objectId = RequestParser.GetObjectIdFromQuery(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync<SessionModel>(
            _logger,
            nameof(StartQuickBackupJobAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                if (!Enum.TryParse<EVmwareInventoryType>(viType, ignoreCase: true, out var enumedViType))
                    _logger.LogError($"'{viType}' is not a valid {typeof(EVmwareInventoryType).Name}.", nameof(viType));
                var req = new VmwareObjectModel()
                {
                    Type = enumedViType,
                    HostName = vmHostName,
                    Name = vmName,
                    ObjectId = objectId,
                    Platform = EPlatformType.VMware
                };
                return await client.StartQuickBackupAsync(req);
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }

    [Function("GetBackupObjectByIdAsync")]
    public async Task<IActionResult> GetBackupObjectByIdAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        _logger.LogInformation($"Calling {nameof(GetBackupObjectByIdAsync)} Azure Function was triggered with query parameters {request.QueryString}");

        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);
        var machineBackupObjectId = RequestParser.GetBackupObjectId(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(GetBackupObjectByIdAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                return (ViBackupObjectModel)await client.GetBackupObjectByIdAsync(machineBackupObjectId);
            },

            resp =>
            {
                if (resp.ViType == null)
                    return Task.FromResult<IActionResult>(new ObjectResult("An unexpected error occurred. See server logs for details.") { StatusCode = StatusCodes.Status500InternalServerError });

                var dto = new BackupObjectDTO { VmHostName = BackupObjectHelper.ExtractHostName(resp.Path), VmName = resp.Name, ViType = resp.ViType.Value.ToString(), ObjectId = resp.ObjectId };
                return Task.FromResult<IActionResult>(new OkObjectResult(dto));
            }
        );
    }

}