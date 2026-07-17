using System.Collections.Concurrent;
using Microsoft.Extensions.Logging;
using Sentinel.Client;

namespace Sentinel.Managers
{
    class CovewareConnectionsManagerImpl : ICovewareConnectionsManager
    {
        private readonly ISecretsManager _secretsManager;
        private readonly ConcurrentDictionary<string, ICovewareClient> _idToClient = new();
        private readonly ILogger<AuthenticatedCovewareClientHandler> _logger;

        public CovewareConnectionsManagerImpl(ISecretsManager secretsManager, ILogger<AuthenticatedCovewareClientHandler> logger)
        {
            _secretsManager = secretsManager ?? throw new ArgumentNullException(nameof(secretsManager));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        public async Task<ICovewareClient> GetOrCreateAsync(string covewareId)
        {
            _logger.LogInformation($"Calling {nameof(GetOrCreateAsync)} was called for \"{covewareId}\"");

            if (string.IsNullOrEmpty(covewareId))
                throw new ArgumentException($"'{nameof(covewareId)}' cannot be null or empty.", nameof(covewareId));

            if (_idToClient.TryGetValue(covewareId, out ICovewareClient? client))
            {
                _logger.LogInformation($"Client for \"{covewareId}\" was found.");
                return client;
            }

            _logger.LogInformation($"No client for \"{covewareId}\" was found, creating it..");

            var baseUrl = await _secretsManager.GetCovewareAuthUrlAsync(covewareId);

            client = new CovewareClientImpl(baseUrl, covewareId, _secretsManager, _logger);

            _idToClient[covewareId] = client;

            _logger.LogInformation($"Client for \"{covewareId}\" created and saved to the dictionary.");

            return client;
        }
    }
}