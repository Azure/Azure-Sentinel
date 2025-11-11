using Microsoft.Extensions.Logging;
using System.IO;
using System.Threading.Tasks;

namespace Varonis.Sentinel.Functions.LogAnalytics
{
    internal class LogAnalyticsFake : ILogAnalyticsStorage
    {
        private const string FileName = "LogAnalyticsFakes.log";
        private readonly ILogger _logger;

        public LogAnalyticsFake(ILogger logger)
        {
            _logger = logger;
            var fi = new FileInfo(FileName);
            _logger.LogInformation(fi.FullName);
        }

        public async Task PublishAsync(string data)
        {
            using var writer = new StreamWriter(FileName, true);
            
            await writer.WriteAsync(data);
        }
    }
}
