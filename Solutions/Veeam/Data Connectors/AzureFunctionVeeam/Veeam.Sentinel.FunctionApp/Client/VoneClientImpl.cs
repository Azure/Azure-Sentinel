using Microsoft.Extensions.Logging;
using Sentinel.Managers;
using VoneApiClient;
using VoneApiClient.Models;

namespace Sentinel.Client
{
    public class VoneClientImpl : AuthenticatedVoneClientHandler, IVoneClient
    {
        private readonly ITriggeredAlarmsApi _triggeredAlarmsApi;
        private readonly string _voneId;

        public VoneClientImpl(string baseUrl, string voneId, ISecretsManager secretsManager, ILogger<AuthenticatedVoneClientHandler> logger)
            : base(baseUrl, voneId, secretsManager, logger)
        {
            _voneId = voneId;
            _triggeredAlarmsApi = new TriggeredAlarmsApi(_voneConfig, logger);
        }

        public async Task<List<TriggeredAlarm>> GetTriggeredAlarmsAsync(TriggeredAlarmFilter filter)
        {
            _logger.LogInformation($"{nameof(GetTriggeredAlarmsAsync)} called for \"{_voneId}\" with Offset={filter.Offset}, Limit={filter.Limit}");
            var response = await SendAsync(async (cancellationToken) => await _triggeredAlarmsApi.GetTriggeredAlarmsAsync(filter), default);
            _logger.LogInformation($"{nameof(GetTriggeredAlarmsAsync)} response fetched \"{_voneId}\": {response.Count} events.");
            return response;
        }

        public Task ResolveTriggeredAlarmAsync(int predefinedAlaramId)
        {
            _logger.LogInformation($"{nameof(ResolveTriggeredAlarmAsync)} called for \"{_voneId}\" with PredefinedAlarmId={predefinedAlaramId}");

            return SendAsync(async _ =>
            {
                await _triggeredAlarmsApi.ResolveTriggeredAlarmAsync(predefinedAlaramId);
                return Task.CompletedTask; 
            }, default);
        }
    }
}
