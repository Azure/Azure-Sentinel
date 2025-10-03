using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.Extensions.Logging;
using Sentinel.Constants;
using Sentinel.DTOs;

namespace Sentinel.Managers
{
    class SecretsManagerImpl : ISecretsManager
    {
        private readonly SecretClient _keyVaultSecretClient;
        private readonly ISettingsManager _vbrSettingManager;
        private readonly ILogger<SecretsManagerImpl> _logger;

        public SecretsManagerImpl(ILogger<SecretsManagerImpl> logger)
        {
            var kvName = Environment.GetEnvironmentVariable(EnvironmentVariablesConstants.KeyVaultNameLabel) ?? throw new InvalidOperationException($"The environment variable {EnvironmentVariablesConstants.KeyVaultNameLabel} is not set.");
            
            var kvUri = EnvironmentVariablesConstants.CreateKeyVaultUri(kvName);

            _keyVaultSecretClient = new SecretClient(new Uri(kvUri), new DefaultAzureCredential());

            _vbrSettingManager = new WatchListSettingsManager(logger);

            _logger = logger;
        }


        public async Task<Credentials> GetVbrCredentialsAsync(string vbrId)
        {
            _logger.LogInformation($"Calling {nameof(GetVbrCredentialsAsync)} for \"{vbrId}\"");
            var passwordSecretAlias = await _vbrSettingManager.GetVbrPasswordAliasAsync(vbrId);
            var usernameSecretAlias = await _vbrSettingManager.GetVbrUsernameAliasAsync(vbrId);

            _logger.LogInformation($"Getting credentials' values for \"{vbrId}\" from keyvault");
            var passwordSecret = await _keyVaultSecretClient.GetSecretAsync(passwordSecretAlias.Trim());
            var usernameSecret = await _keyVaultSecretClient.GetSecretAsync(usernameSecretAlias.Trim());

            var passwordSecretValue = passwordSecret.Value;
            var usernameSecretValue = usernameSecret.Value;

            if (string.IsNullOrEmpty(passwordSecretValue.Value) || string.IsNullOrEmpty(usernameSecretValue.Value))
                throw new KeyNotFoundException("passwordSecretValue or usernameSecretValue is null or empty");

            if (string.Equals(passwordSecretValue.Value, "UNDEFINED", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"Password for VBR '{vbrId}' is set to 'UNDEFINED'. Please set the actual password value in Azure Key Vault for secret '{passwordSecretAlias}'.");

            _logger.LogInformation($"Credentials' values for \"{vbrId}\" successfuly got");
            return new Credentials(usernameSecretValue.Value, passwordSecretValue.Value);
        }


        public async Task SaveTokensAsync(string vbrId, Tokens tokens)
        {
            _logger.LogInformation($"Calling {nameof(SaveTokensAsync)} for \"{vbrId}\"");

            var accessTokenAlias = "access-token-" + vbrId;
            var refreshTokenAlias = "refresh-token-" + vbrId;

            await _keyVaultSecretClient.SetSecretAsync(accessTokenAlias, tokens.AccessToken);
            await _keyVaultSecretClient.SetSecretAsync(refreshTokenAlias, tokens.RefreshToken);

            _logger.LogInformation($"Saved tokens for \"{vbrId}\" to KeyVault");
        }

        public async Task<Tokens> GetTokensAsync(string vbrId)
        {
            _logger.LogInformation($"Calling {nameof(GetTokensAsync)} for \"{vbrId}\"");

            var accessTokenAlias = "access-token-" + vbrId;
            var refreshTokenAlias = "refresh-token-" + vbrId;

            var accessTokenSecret = await _keyVaultSecretClient.GetSecretAsync(accessTokenAlias);
            var refreshTokenSecret = await _keyVaultSecretClient.GetSecretAsync(refreshTokenAlias);

            var accessTokenValue = accessTokenSecret.Value;
            var refreshTokenValue = refreshTokenSecret.Value;

            if (string.IsNullOrEmpty(accessTokenValue.Value) || string.IsNullOrEmpty(refreshTokenValue.Value))
                throw new KeyNotFoundException("accessTokenValue or refreshTokenValue is null or empty");

            _logger.LogInformation($"Current tokens for \"{vbrId}\" retrieved from keyVault.");

            return new Tokens(accessTokenValue.Value, refreshTokenValue.Value);
        }

        public async Task<string> GetVbrBaseUrlAsync(string vbrId)
        {
            return await _vbrSettingManager.GetVbrBaseUrlAsync(vbrId);
        }

        public async Task<Credentials> GetVoneCredentialsAsync(string voneId)
        {
            _logger.LogInformation($"Calling {nameof(GetVoneCredentialsAsync)} for \"{voneId}\"");
            var passwordSecretAlias = await _vbrSettingManager.GetVonePasswordAliasAsync(voneId);
            var usernameSecretAlias = await _vbrSettingManager.GetVoneUsernameAliasAsync(voneId);

            _logger.LogInformation($"Getting credentials' values for \"{voneId}\" from keyvault");
            var passwordSecret = await _keyVaultSecretClient.GetSecretAsync(passwordSecretAlias.Trim());
            var usernameSecret = await _keyVaultSecretClient.GetSecretAsync(usernameSecretAlias.Trim());

            var passwordSecretValue = passwordSecret.Value;
            var usernameSecretValue = usernameSecret.Value;

            if (string.IsNullOrEmpty(passwordSecretValue.Value) || string.IsNullOrEmpty(usernameSecretValue.Value))
                throw new KeyNotFoundException("passwordSecretValue or usernameSecretValue is null or empty");

            if (string.Equals(passwordSecretValue.Value, "UNDEFINED", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"Password for VONE '{voneId}' is set to 'UNDEFINED'. Please set the actual password value in Azure Key Vault for secret '{passwordSecretAlias}'.");

            _logger.LogInformation($"Credentials' values for \"{voneId}\" successfuly got");
            return new Credentials(usernameSecretValue.Value, passwordSecretValue.Value);
        }

        public async Task<string> GetVoneBaseUrlAsync(string voneId)
        {
            return await _vbrSettingManager.GetVoneBaseUrlAsync(voneId);
        }

        public async Task<CovewareCredentials> GetCowareCredentialsAsync(string cowareId)
        {
            _logger.LogInformation($"Calling {nameof(GetCowareCredentialsAsync)} for \"{cowareId}\"");
         
            var passwordSecretAlias = await _vbrSettingManager.GetCovewarePasswordAliasAsync(cowareId);
            var usernameSecretAlias = await _vbrSettingManager.GetCovewareUsernameAliasAsync(cowareId);
            var clientIdSecretAlias = await _vbrSettingManager.GetCovewareClientIdAliasAsync(cowareId);

            _logger.LogInformation($"Getting credentials' values for \"{cowareId}\" from keyvault");
            var passwordSecret = await _keyVaultSecretClient.GetSecretAsync(passwordSecretAlias.Trim());
            var usernameSecret = await _keyVaultSecretClient.GetSecretAsync(usernameSecretAlias.Trim());
            var clientIdSecret = await _keyVaultSecretClient.GetSecretAsync(clientIdSecretAlias.Trim());

            var passwordSecretValue = passwordSecret.Value;
            var usernameSecretValue = usernameSecret.Value;
            var clientIdSecretValue = clientIdSecret.Value;

            if (string.IsNullOrEmpty(passwordSecretValue.Value) || string.IsNullOrEmpty(usernameSecretValue.Value) || string.IsNullOrEmpty(clientIdSecretValue.Value))
                throw new KeyNotFoundException("passwordSecretValue, usernameSecretValue, or clientIdSecretValue is null or empty");

            if (string.Equals(passwordSecretValue.Value, "UNDEFINED", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"Password for Coveware '{cowareId}' is set to 'UNDEFINED'. Please set the actual password value in Azure Key Vault for secret '{passwordSecretAlias}'.");

            if (string.Equals(clientIdSecretValue.Value, "UNDEFINED", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"ClientId for Coveware '{cowareId}' is set to 'UNDEFINED'. Please set the actual client ID value in Azure Key Vault for secret '{clientIdSecretAlias}'.");

            _logger.LogInformation($"Credentials' values for \"{cowareId}\" successfuly got");
            return new CovewareCredentials(usernameSecretValue.Value, passwordSecretValue.Value, clientIdSecretValue.Value);
        }

        public async Task SaveCovewareTokensAsync(string covewareId, CovewareTokens tokens)
        {
            _logger.LogInformation($"Calling {nameof(SaveCovewareTokensAsync)} for \"{covewareId}\"");

            var accessTokenAlias = "access-token-" + covewareId;
            var refreshTokenAlias = "refresh-token-" + covewareId;
            var idTokenAlias = "id-token-" + covewareId;

            await _keyVaultSecretClient.SetSecretAsync(accessTokenAlias, tokens.AccessToken);
            
            if (tokens.RefreshToken != null) // when refreshing tokens, refreshToken stays
                await _keyVaultSecretClient.SetSecretAsync(refreshTokenAlias, tokens.RefreshToken);
            
            await _keyVaultSecretClient.SetSecretAsync(idTokenAlias, tokens.IdToken);

            _logger.LogInformation($"Saved Coveware tokens for \"{covewareId}\" to KeyVault");
        }

        public async Task<CovewareTokens> GetCovewareTokensAsync(string covewareId)
        {
            _logger.LogInformation($"Calling {nameof(GetCovewareTokensAsync)} for \"{covewareId}\"");

            var accessTokenAlias = "access-token-" + covewareId;
            var refreshTokenAlias = "refresh-token-" + covewareId;
            var idTokenAlias = "id-token-" + covewareId;

            var accessTokenSecret = await _keyVaultSecretClient.GetSecretAsync(accessTokenAlias);
            var refreshTokenSecret = await _keyVaultSecretClient.GetSecretAsync(refreshTokenAlias);
            var idTokenSecret = await _keyVaultSecretClient.GetSecretAsync(idTokenAlias);

            var accessTokenValue = accessTokenSecret.Value;
            var refreshTokenValue = refreshTokenSecret.Value;
            var idTokenValue = idTokenSecret.Value;

            if (string.IsNullOrEmpty(accessTokenValue.Value) || string.IsNullOrEmpty(refreshTokenValue.Value) ||
                string.IsNullOrEmpty(idTokenValue.Value))
                throw new KeyNotFoundException("Coveware accessToken, refreshToken, or idToken is null or empty");

            _logger.LogInformation($"Current Coveware tokens for \"{covewareId}\" retrieved from keyVault.");

            return new CovewareTokens(accessTokenValue.Value, refreshTokenValue.Value, idTokenValue.Value);
        }

        public async Task<string> GetCovewareAuthUrlAsync(string covewareId)
        {
            return await _vbrSettingManager.GetCovewareBaseUrlAsync(covewareId);
        }
    }
}