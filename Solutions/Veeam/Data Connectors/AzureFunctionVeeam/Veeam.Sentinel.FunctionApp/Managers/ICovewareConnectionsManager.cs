using Sentinel.Client;

namespace Sentinel.Managers
{
    public interface ICovewareConnectionsManager
    {
        Task<ICovewareClient> GetOrCreateAsync(string covewareId);
    }
}
