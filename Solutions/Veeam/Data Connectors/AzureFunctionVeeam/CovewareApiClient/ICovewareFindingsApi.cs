using CovewareApiClient.Models;

namespace CovewareApiClient
{
    public interface ICovewareFindingsApi
    {
        Task<CovewareFindingsResponse> GetFindingsAsync(CovewareFindingFilter filter);
    }
}