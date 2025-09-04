
using VoneApiClient.Models;

namespace VoneApiClient
{
    public interface ILoginApi
    {
        Task<VoneTokenModel> CreateTokenAsync(TokenLoginSpec tokenLoginSpec);
    }
}
