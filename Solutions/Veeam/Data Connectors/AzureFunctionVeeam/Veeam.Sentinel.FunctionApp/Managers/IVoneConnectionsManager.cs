using System.Threading.Tasks;
using Sentinel.Client;

namespace Sentinel.Managers
{
    public interface IVoneConnectionsManager
    {
        Task<IVoneClient> GetOrCreateAsync(string voneId);
    }
}
