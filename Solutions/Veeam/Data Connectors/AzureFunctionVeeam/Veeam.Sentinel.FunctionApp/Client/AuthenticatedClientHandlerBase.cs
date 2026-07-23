using Microsoft.Extensions.Logging;
using Sentinel.Managers;

namespace Sentinel.Client
{
    public abstract class AuthenticatedClientHandlerBase : IDisposable
    {
        private readonly SemaphoreSlim _refreshTokenSync = new(1, 1);
        protected readonly ISecretsManager _secretsManager;
        protected readonly string _clientId;
        protected readonly ILogger _logger;

        protected AuthenticatedClientHandlerBase(string clientId, ISecretsManager secretsManager, ILogger logger)
        {
            if (string.IsNullOrEmpty(clientId))
                throw new ArgumentException($"'{nameof(clientId)}' cannot be null or empty.", nameof(clientId));

            _clientId = clientId;
            _secretsManager = secretsManager ?? throw new ArgumentNullException(nameof(secretsManager));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        }

        protected abstract bool IsTokenPresent();

        protected abstract Task CreateNewTokensUsingUsernamePasswordAsync();

        protected abstract Task RefreshTokenInternalAsync(CancellationToken cancellationToken);

        protected abstract bool IsUnauthorizedException(Exception ex);

        protected virtual async Task<TResponse> ExecuteRequestAsync<TResponse>(Func<CancellationToken, Task<TResponse>> request, CancellationToken cancellationToken)
        {
            return await request(cancellationToken);
        }

        protected async Task<TResponse> SendAsync<TResponse>(Func<CancellationToken, Task<TResponse>> request, CancellationToken cancellationToken)
        {
            _logger.LogInformation($"Calling {nameof(SendAsync)} for \"{_clientId}\"");

            try
            {
                await InitialTokenCheckAsync();
            }
            catch (Exception ex)
            {
                if (IsUnauthorizedException(ex))
                    _logger.LogError(ex, $"Invalid username or password set for \"{_clientId}\", check settings. Error details:  {ex.Message}");
                else
                    _logger.LogError(ex, $"Error occurred when calling api/token for \"{_clientId}\". Error details: {ex.Message}");
                throw;
            }

            try
            {
                _logger.LogInformation($"Trying to perform request for \"{_clientId}\"");

                var result = await ExecuteRequestAsync(request, cancellationToken);

                _logger.LogInformation($"Successfully called request for \"{_clientId}\"");

                return result;
            }
            catch (Exception ex) when (IsUnauthorizedException(ex))
            {
                _logger.LogInformation($"Unauthorized exception caught, access_token expired for \"{_clientId}\"");

                await RefreshTokenAsync(cancellationToken);

                return await ExecuteRequestAsync(request, cancellationToken);
            }
        }


        protected async Task InitialTokenCheckAsync()
        {
            _logger.LogInformation($"Calling {nameof(InitialTokenCheckAsync)} for \"{_clientId}\"");

            if (IsTokenPresent())
            {
                _logger.LogInformation($"Token is valid for \"{_clientId}\", InitialTokenCheckAsync will not be performed");
                return;
            }

            await _refreshTokenSync.WaitAsync();
            try
            {
                _logger.LogInformation($"Token is invalid for \"{_clientId}\", calling CreateNewTokensUsingUsernamePassword");
                await CreateNewTokensUsingUsernamePasswordAsync();
            }
            finally
            {
                _refreshTokenSync.Release();
            }
        }

        private async Task RefreshTokenAsync(CancellationToken cancellationToken = default)
        {
            _logger.LogInformation($"Calling {nameof(RefreshTokenAsync)} for \"{_clientId}\"");

            await _refreshTokenSync.WaitAsync(cancellationToken);
            try
            {
                await RefreshTokenInternalAsync(cancellationToken);
            }
            catch (Exception ex) when (IsUnauthorizedException(ex))
            {
                _logger.LogInformation($"Refresh token expired for \"{_clientId}\"");
                await CreateNewTokensUsingUsernamePasswordAsync();
            }
            finally
            {
                _refreshTokenSync.Release();
            }
        }

        public virtual void Dispose()
        {
            _refreshTokenSync?.Dispose();
        }
    }
}