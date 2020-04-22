using Microsoft.Azure.KeyVault;
using Microsoft.Azure.KeyVault.Models;
using Microsoft.Azure.Services.AppAuthentication;
using System;
using System.Globalization;
using System.Linq;
using System.Runtime.Caching;
using System.Threading.Tasks;

namespace Teams.CustomConnector.Common
{
    public class KeyVaultHelper
    {
        //Azure Functions are stateless in nature. Therefore even though we use the standard.Net objects to cache values, 
        //they don’t persist if the Azure Function scales out or is idle for some time.
        //In consumption plan, functionTimeout is 10 minutes (max).
        //for app service plan its configurable as per platform and will persists cache for the configuered time.

        //Available approaches
        //1. In memory using standard dotnet objects, downside of using this approach is, during scale out operation it will be again reach out to external endpoint. 
        //2. using external (Redis) 
        //3. External storage options (table/blobs) etc, This will require encryption/Decryption logic along with implementation of push/pull mechanism

        //This lightweight keyvaulthelper is will use option 1 for caching during the available functionapp lifetime

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
                KeyVaultClient keyVaultClient = new KeyVaultClient(new KeyVaultClient.AuthenticationCallback(new AzureServiceTokenProvider().KeyVaultTokenCallback));
                SecretBundle secretBundle = null;

                await retryWithExponentialBackoff.RunAsync(async () =>
                {
                    secretBundle = await keyVaultClient.GetSecretAsync($"{baseUrl}/secrets/{key}");
                });

                return secretBundle?.Value;
            }
            catch (System.Exception ex)
            {
                throw ex;
            }
        }
     
    }
}
