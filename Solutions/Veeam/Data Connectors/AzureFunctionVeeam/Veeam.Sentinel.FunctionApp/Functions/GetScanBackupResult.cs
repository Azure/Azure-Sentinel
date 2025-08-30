using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Sentinel.Helpers;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;

namespace Sentinel.Functions;

public class GetScanBackupResult
{
    private readonly IVbrConnectionsManager _vbrConnectionsManager;
    private readonly ILogger<GetScanBackupResult> _logger;

    public GetScanBackupResult(ILogger<GetScanBackupResult> logger, IVbrConnectionsManager vbrConnectionsManager)
    {
        _vbrConnectionsManager = vbrConnectionsManager;

        _logger = logger;
    }

    [Function("StartBackupScanAV")]
    public async Task<IActionResult> StartScanBackupAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);
        var backupObjectId = RequestParser.GetBackupObjectId(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(StartScanBackupAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                // Get backupObjectId from /api/v1/backupObjects/{id}
                var backupObject = await client.GetBackupObjectRestorePointsAsync(backupObjectId);

                var backupId = GetLastCleanRestorePoint(backupObject);

                if (backupId == Guid.Empty)
                    throw new InvalidOperationException($"No clean restore point could be retrieved for backup object with ID: {backupObjectId}.");

                // scanBackup by calling POST on /api/v1/malwareDetection/scanBackup
                var startBackupResponse = await client.StartScanBackupAsync(backupObjectId, backupId);

                return startBackupResponse.Id;
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(new { sessionId = resp }))
        );
    }

    private Guid GetLastCleanRestorePoint(ObjectRestorePointsResult backupObject)
    {
        // they are sorted by time, so first clean will be latest
        foreach (var restorePoint in backupObject.Data)
        {
            var status = restorePoint.MalwareStatus;

            if (status == ESuspiciousActivitySeverity.Clean)
                return restorePoint.BackupId;
        }

        return Guid.Empty;
    }


    [Function("GetSessionAsync")]
    public async Task<IActionResult> GetSessionAsync([HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest request)
    {
        var vbrHostName = RequestParser.GetVbrHostNameFromQuery(request);
        var sessionId = RequestParser.GetSessionId(request);

        var client = await _vbrConnectionsManager.GetOrCreateAsync(vbrHostName);

        return await FunctionErrorHandler.ExecuteAsync(
            _logger,
            nameof(GetSessionAsync),
            request.QueryString.ToString(),
            vbrHostName,

            async () =>
            {
                return await client.GetSessionAsync(sessionId);
            },

            resp => Task.FromResult<IActionResult>(new OkObjectResult(resp))
        );
    }
}