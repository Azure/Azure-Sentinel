using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.Azure.Services.AppAuthentication;
using System;
using System.Runtime.Caching;
using System.Threading.Tasks;

namespace Teams.CustomConnector.Common
{
    public class KeyVaultHelper
    {
        static readonly ObjectCache secretCache = MemoryCache.Default;
        private static readonly RetryWithExponentialBackoff retryWithExponentialBackoff = new RetryWithExponentialBackoff(5);

        /// <summary>Gets the key value asynchronous.</summary>
        /// <param name="key">The key.</param>
        /// <returns></returns>
        public static async Task<string> GetKeyValueAsync(string key)
        {
            string secretValue;
            if (Convert.ToBoolean(Environment.GetEnvironmentVariable(Constants.KeyVaultEnabled)) && !string.IsNullOrWhiteSpace(key) )
            {
                CacheItem cacheContents = secretCache.GetCacheItem(key);
                if (cacheContents == null)
                {
                    // cache doesn’t exist. Add key to cache.
                    CacheItemPolicy policy = new CacheItemPolicy
                    {
                        Priority = CacheItemPriority.Default,
                        // Setting expiration timing for the cache, although doesn't make sense in consumption plan
                        // for ASP , we can get this value from config, to get more control
                        AbsoluteExpiration = DateTimeOffset.Now.AddHours(24)
                    };

                    secretValue = await LoadKeysFromVault(key);

                    cacheContents = new CacheItem(key, secretValue);
                    secretCache.Set(cacheContents, policy);
                }
                else
                {
                    secretValue = cacheContents.Value.ToString();
                }
            }
            else
            {
                secretValue = key;
            }
            return secretValue;
        }



        /// <summary>Loads the keys from vault.</summary>
        /// <param name="key">The key.</param>
        /// <returns></returns>
        private static async Task<string> LoadKeysFromVault(string key)
        {
            try
            {
                var baseUrl = Environment.GetEnvironmentVariable(Constants.KeyVaultBaseUrl);
                SecretClient secretClient = new SecretClient(new Uri(baseUrl), new DefaultAzureCredential());
                KeyVaultSecret keyVaultSecret = null;

                await retryWithExponentialBackoff.RunAsync(async () =>
                {
                    keyVaultSecret = await secretClient.GetSecretAsync(key);
                });

                return keyVaultSecret.Value;
            }
            catch (System.Exception ex)
            {
                throw ex;
            }
        }
     
    }
}
