using CovewareApiClient.Models;

namespace Sentinel.Client;

public interface ICovewareClient
{
    Task<CovewareFindingsResponse> GetCovewareFindingsAsync();
}