using CovewareApiClient.Models;

namespace CovewareApiClient
{
    public interface ICovewareLoginApi
    {
        Task<CovewareAuthResponse> CreateTokenAsync(ICovewareAuthRequest authRequest);
    }
}