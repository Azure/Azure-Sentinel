using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Sentinel.Client;

namespace Sentinel.Managers
{
    public class VoneConnectionsManagerImpl : IVoneConnectionsManager
    {
        private readonly ISecretsManager _secretsManager;
        private readonly ConcurrentDictionary<string, IVoneClient> _idToClient = new();
        private readonly ILogger<AuthenticatedVoneClientHandler> _logger;

        public VoneConnectionsManagerImpl(ISecretsManager secretsManager, ILogger<AuthenticatedVoneClientHandler> logger)
        {
            _secretsManager = secretsManager ?? throw new ArgumentNullException(nameof(secretsManager));
            _logger = logger;
        }

        public async Task<IVoneClient> GetOrCreateAsync(string voneId)
        {
            _logger.LogInformation($"Calling {nameof(GetOrCreateAsync)} was called for \"{voneId}\"");

            if (string.IsNullOrEmpty(voneId))
                throw new ArgumentException($"'{nameof(voneId)}' cannot be null or empty.", nameof(voneId));

            if (_idToClient.TryGetValue(voneId, out IVoneClient? client))
            {
                _logger.LogInformation($"Client for \"{voneId}\" was found.");
                return client;
            }

            _logger.LogInformation($"No client for \"{voneId}\" was found, creating it..");

            var baseUrl = await _secretsManager.GetVoneBaseUrlAsync(voneId);

            client = new VoneClientImpl(baseUrl, voneId, _secretsManager, _logger);

            _idToClient[voneId] = client;

            _logger.LogInformation($"Client for \"{voneId}\" created and saved to the dictionary.");

            return client;
        }
    }
}
