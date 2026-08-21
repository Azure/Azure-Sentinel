using Microsoft.Extensions.Logging;
using Sentinel.Client;
using Sentinel.Managers;

namespace Veeam.Sentinel.FunctionApp.Tests.Client
{
    public class TestableAuthenticatedVoneClientHandler : AuthenticatedVoneClientHandler
    {
        public TestableAuthenticatedVoneClientHandler(
            string baseUrl,
            string voneId,
            ISecretsManager secretsManager,
            ILogger<AuthenticatedVoneClientHandler> logger
        ) : base(baseUrl, voneId, secretsManager, logger)
        {
        }

        public bool HasCustomServerCertificateValidationCallback =>
            _httpClientHandler.ServerCertificateCustomValidationCallback != null;
    }
}
