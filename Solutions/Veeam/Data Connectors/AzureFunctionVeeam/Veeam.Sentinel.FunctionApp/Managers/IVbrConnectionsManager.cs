using Sentinel.Client;

namespace Sentinel.Managers
{
    public interface IVbrConnectionsManager
    {
        Task<IVbrClient> GetOrCreateAsync(string vbrId);
    }
}
