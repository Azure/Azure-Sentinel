using Microsoft.Extensions.Logging;
using Sentinel.Client;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1;

namespace Veeam.Sentinel.FunctionApp.Tests.Client
{
    public class TestableAuthenticatedVbrClientHandler : AuthenticatedVbrClientHandler
    {
        public TestableAuthenticatedVbrClientHandler(
            ILoginApi loginApi,
            string baseUrl,
            string vbrId,
            ISecretsManager secretsManager,
            ILogger<AuthenticatedVbrClientHandler> logger
        ) : base(loginApi, baseUrl, vbrId, secretsManager, logger)
        {
        }

        public Task<T> InvokeSendAsync<T>(Func<CancellationToken, Task<T>> request, CancellationToken cancellationToken)
        {
            return SendAsync(request, cancellationToken);
        }
    }
}
