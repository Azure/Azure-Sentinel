﻿using CovewareApiClient;
using CovewareApiClient.Models;
using Microsoft.Extensions.Logging;
using Sentinel.Managers;

namespace Sentinel.Client;

public class CovewareClientImpl: AuthenticatedCovewareClientHandler, ICovewareClient
{
    private readonly ICovewareFindingsApi _covewareFindingsApi;
    
    public CovewareClientImpl(string baseUrl, string covewareId, ISecretsManager secretsManager,
        ILogger<AuthenticatedCovewareClientHandler> logger) : base(baseUrl, covewareId, secretsManager, logger)
    {
        _covewareFindingsApi = new CovewareFindingsApi(_apiConfig, logger);
    }

    public async Task<CovewareFindingsResponse> GetCovewareFindingsAsync(CovewareFindingFilter filter)
    {
        _logger.LogInformation($"{nameof(GetCovewareFindingsAsync)} called");

        var response = await SendAsync(async (cancellationToken) => await _covewareFindingsApi.GetFindingsAsync(filter), default);
        _logger.LogInformation($"{nameof(GetCovewareFindingsAsync)} response fetched {response.Data.Count} events");
        return response;
    }
}