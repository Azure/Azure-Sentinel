using System;
using System.Collections;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Net.Http;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Threading.Tasks;
using Microsoft.IdentityModel.Tokens;
using Newtonsoft.Json;
using Octokit;

namespace Kqlvalidations.Tests
{
    public sealed class GitHubApiClient
    {
        private static GitHubApiClient _instance;
        private static readonly object _lock = new object();
        private readonly GitHubClient _client;

        private string _owner = "Azure";
        private string _repo = "Azure-Sentinel";
        private int? _prNumber;
        private IReadOnlyList<PullRequestFile> _cachedPullRequestFiles;

        

        private GitHubApiClient(string accessToken)
        {
            var credentials = new Credentials(accessToken);
            _client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            _client.Credentials = credentials;
        }

        public static GitHubApiClient Create()
        {
            //write all env variables to console
            foreach (DictionaryEntry de in Environment.GetEnvironmentVariables())
            {
                Console.WriteLine("  {0} = {1}", de.Key, de.Value);
            }

            if (_instance == null)
            {
                lock (_lock)
                {
                    if (_instance == null)
                    {
                        var appId = Environment.GetEnvironmentVariable("GITHUBAPPID111");
                        var installationId = Environment.GetEnvironmentVariable("GITHUBAPPINSTALLATIONID111");
                        var privateKey = Environment.GetEnvironmentVariable("GITHUBAPPPRIVATEKEY111");

                        if (string.IsNullOrEmpty(appId) || string.IsNullOrEmpty(installationId) || string.IsNullOrEmpty(privateKey))
                        {
                            Console.WriteLine($"GitHub App ID: {appId}");
                            Console.WriteLine($"Installation ID: {installationId}");
                            Console.WriteLine($"Private Key: {privateKey}");

                            throw new InvalidOperationException("GitHub App ID, Installation ID, or Private Key is missing.");
                        }

                        var jwtToken = GenerateJwtToken(appId, RemovePemHeaderAndFooter(privateKey));
                        var accessToken = GetInstallationAccessToken(appId, installationId, jwtToken).Result;
                        _instance = new GitHubApiClient(accessToken);
                    }
                }
            }
            return _instance;
        }

        public void SetRepositoryDetails(string owner, string repo)
        {
            _owner = owner;
            _repo = repo;
        }

        public IReadOnlyList<PullRequestFile> GetPullRequestFiles()
        {
            if (_cachedPullRequestFiles == null)
            {
                try
                {
                    _cachedPullRequestFiles = _client.PullRequest.Files(_owner, _repo, GetPullRequestNumber()).Result;
                }
                catch (Exception ex)
                {
                    HandleException("Error occurred while getting PR files", ex);
                    _cachedPullRequestFiles = new List<PullRequestFile>();
                }
            }

            return _cachedPullRequestFiles;
        }

        public void AddPRComment(string comment)
        {
            try
            {
                int prNumber = GetPullRequestNumber();
                if (prNumber == 0)
                {
                    Console.WriteLine("PR number not available. Cannot add comment.");
                    return;
                }

                var pullRequestReviewCreate = new PullRequestReviewCreate
                {
                    Body = comment,
                    Event = PullRequestReviewEvent.Comment
                };

                var newComment = _client.PullRequest.Review.Create(_owner, _repo, prNumber, pullRequestReviewCreate).Result;
            }
            catch (Exception ex)
            {
                HandleException("Error occurred while adding PR comment", ex);
            }
        }

        private static string RemovePemHeaderAndFooter(string privateKey)
        {
            const string header = "-----BEGIN RSA PRIVATE KEY-----";
            const string footer = "-----END RSA PRIVATE KEY-----";

            int start = privateKey.IndexOf(header) + header.Length;
            int end = privateKey.IndexOf(footer, start);

            return privateKey.Substring(start, end - start).Replace("\r", "").Replace("\n", "");
        }

        private static string GenerateJwtToken(string appId, string privateKey)
        {
            using (RSA rsa = RSA.Create())
            {
                rsa.ImportRSAPrivateKey(Convert.FromBase64String(privateKey), out _);

                var now = DateTimeOffset.UtcNow;
                var expiration = now.AddMinutes(10); // Adjust the expiration time as needed

                var signingCredentials = new SigningCredentials(new RsaSecurityKey(rsa), SecurityAlgorithms.RsaSha256);

                var claims = new[]
                {
                new Claim("iat", now.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer),
                new Claim("exp", expiration.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer),
                new Claim("iss", appId)
            };

                var token = new JwtSecurityToken(claims: claims, signingCredentials: signingCredentials);
                var handler = new JwtSecurityTokenHandler();

                return handler.WriteToken(token);
            }
        }

        private static async Task<string> GetInstallationAccessToken(string appId, string installationId, string jwtToken)
        {
            var installationUrl = $"https://api.github.com/app/installations/{installationId}/access_tokens";
            var httpClient = new HttpClient();

            httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {jwtToken}");
            httpClient.DefaultRequestHeaders.Add("Accept", "application/vnd.github.v3+json");
            httpClient.DefaultRequestHeaders.Add("User-Agent", "MicrosoftSentinelValidationApp");

            var response = await httpClient.PostAsync(installationUrl, null);
            response.EnsureSuccessStatusCode();

            var content = await response.Content.ReadAsStringAsync();
            dynamic json = JsonConvert.DeserializeObject(content);

            return json.token;
        }

        private void HandleException(string errorMessage, Exception ex)
        {
            Console.WriteLine($"{errorMessage}. Error message: {ex.Message}. Stack trace: {ex.StackTrace}");
        }

        public int GetPullRequestNumber()
        {
            if (_prNumber == null)
            {
                int.TryParse(Environment.GetEnvironmentVariable("PRNUM"), out int prNumber);
                _prNumber = prNumber;
                // Uncomment below for debugging with a PR
                // _prNumber = 9476;
            }

            return _prNumber.GetValueOrDefault();
        }
    }

}
