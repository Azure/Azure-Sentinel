using HTTPDataCollectorAPI;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;

namespace Varonis.Sentinel.Functions.LogAnalytics
{
    internal class LogAnalyticsCollector : ILogAnalyticsStorage
    {
        const string datalertTableName = "VaronisAlerts";
        private readonly string _logAnalyticsKey;
        private readonly string _logAnalyticsWorkspace;
        private readonly ILogger _log;

        public LogAnalyticsCollector(string logAnalyticsKey, string logAnalyticsWorkspace, ILogger log)
        {
            _logAnalyticsKey = logAnalyticsKey;
            _logAnalyticsWorkspace = logAnalyticsWorkspace;
            _log = log;
        }

        public async Task PublishAsync(string data)
        {
            var collector = new Collector(_logAnalyticsWorkspace, _logAnalyticsKey);
            await collector.Collect(datalertTableName, data).ConfigureAwait(false);
            _log.LogInformation("Data was sent to log analytics.");
        }
    }
}
