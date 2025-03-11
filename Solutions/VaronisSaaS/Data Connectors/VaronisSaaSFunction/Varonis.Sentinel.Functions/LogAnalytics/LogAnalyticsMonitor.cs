using System;
using System.Threading.Tasks;

namespace Varonis.Sentinel.Functions.LogAnalytics
{
    internal class LogAnalyticsMonitor : ILogAnalyticsStorage
    {
        public Task PublishAsync(string data)
        {
            throw new NotImplementedException();
        }
    }
}
