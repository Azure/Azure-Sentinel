using System.Threading.Tasks;

namespace Varonis.Sentinel.Functions.LogAnalytics
{
    internal interface ILogAnalyticsStorage
    {
        Task PublishAsync(string data);
    }
}
