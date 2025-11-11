using System.Collections.Concurrent;
using Microsoft.Extensions.Logging;
using Sentinel.Client;

namespace Sentinel.Managers
{
    class VbrConnectionsManagerImpl : IVbrConnectionsManager
    {
        private readonly ISecretsManager _secretsManager;
        private readonly ConcurrentDictionary<string, IVbrClient> _idToClient = new ();
        private readonly ILogger<AuthenticatedVbrClientHandler> _logger;

        public VbrConnectionsManagerImpl(ISecretsManager secretsManager, ILogger<AuthenticatedVbrClientHandler> logger)
        {
            _secretsManager = secretsManager ?? throw new ArgumentNullException(nameof(secretsManager));

            _logger = logger;
        }


        public async Task<IVbrClient> GetOrCreateAsync(string vbrId)
        {
            _logger.LogInformation($"Calling {nameof(GetOrCreateAsync)} was called for \"{vbrId}\"");

            if (string.IsNullOrEmpty(vbrId))
                throw new ArgumentException($"'{nameof(vbrId)}' cannot be null or empty.", nameof(vbrId));

            if (_idToClient.TryGetValue(vbrId, out IVbrClient? client))
            {
                _logger.LogInformation($"Client for \"{vbrId}\" was found.");
                return client;
            }


            _logger.LogInformation($"No client for \"{vbrId}\" was found, creating it..");

            var baseUrl = await _secretsManager.GetVbrBaseUrlAsync(vbrId);

            client = new VbrClientImpl(baseUrl, vbrId, _secretsManager, _logger);

            _idToClient[vbrId] = client;

            _logger.LogInformation($"Client for \"{vbrId}\" created and saved to the dictionary.");

            return client;
        }
    }
}
