using Microsoft.IdentityModel.Tokens;
using Newtonsoft.Json;
using Octokit;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Net.Http;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Threading.Tasks;

namespace Kqlvalidations.Tests
{
    /// <summary>
    /// Class for GitHub API client
    /// </summary>
    public sealed class GitHubApiClient
    {
        private static GitHubApiClient _instance;
        private static readonly object _lock = new object();
        private readonly GitHubClient _client;

        private string _owner = "Azure";
        private string _repo = "Azure-Sentinel";
        private int? _prNumber;
        private IReadOnlyList<PullRequestFile> _cachedPullRequestFiles;

        /// <summary>
        /// Initializes a new instance of the <see cref="GitHubApiClient"/> class.
        /// </summary>
        /// <param name="accessToken">access token</param>
        private GitHubApiClient(string accessToken)
        {
            var credentials = new Credentials(accessToken);
            _client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            _client.Credentials = credentials;
        }

        private GitHubApiClient()
        {
            _client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
        }

        /// <summary>
        /// Creates singleton instance of <see cref="GitHubApiClient"/>
        /// </summary>
        /// <returns>singleton instance of GitHub Client</returns>
        /// <exception cref="InvalidOperationException">Throws an exception if there is an issue with app id, installation id, private key.</exception>
        public static GitHubApiClient Create()
        {
            if (_instance == null)
            {
                lock (_lock)
                {
                    if (_instance == null)
                    {
                        if (IsForkRepo())
                        {
                            _instance = new GitHubApiClient();
                        }
                        else
                        {
                            string appId = Environment.GetEnvironmentVariable("GITHUBAPPID");
                            var installationId = Environment.GetEnvironmentVariable("GITHUBAPPINSTALLATIONID");
                            var privateKey = Environment.GetEnvironmentVariable("GITHUBAPPPRIVATEKEY");
                            if (string.IsNullOrEmpty(appId) || string.IsNullOrEmpty(installationId) || string.IsNullOrEmpty(privateKey))
                            {
                                throw new InvalidOperationException("GitHub App ID, Installation ID, or Private Key is missing.");
                            }

                            try
                            {
                                var jwtToken = GenerateJwtToken(appId, RemovePemHeaderAndFooter(privateKey));
                                var accessToken = GetInstallationAccessToken(installationId, jwtToken).Result;
                                _instance = new GitHubApiClient(accessToken);
                            }
                            catch (Exception ex)
                            {
                                throw new InvalidOperationException("Error occurred while creating GitHubApiClient instance.", ex);
                            }
                        }
                    }
                }
            }
            return _instance;
        }

        /// <summary>
        /// Gets the pull request files.
        /// </summary>
        /// <returns>returns pull request files.</returns>
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

        /// <summary>
        /// Adds PR comment.
        /// </summary>
        /// <param name="comment">comment</param>
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

        /// <summary>
        /// Removes the Pem header and footer
        /// </summary>
        /// <param name="privateKey">priavte key</param>
        /// <returns>returns private key without header and footer</returns>
        private static string RemovePemHeaderAndFooter(string privateKey)
        {
            const string header = "-----BEGIN RSA PRIVATE KEY-----";
            const string footer = "-----END RSA PRIVATE KEY-----";

            int start = privateKey.IndexOf(header) + header.Length;
            int end = privateKey.IndexOf(footer, start);

            return privateKey.Substring(start, end - start).Replace("\r", "").Replace("\n", "");
        }

        /// <summary>
        /// Generates the JWT token with app id and private key
        /// </summary>
        /// <param name="appId">app id</param>
        /// <param name="privateKey">private key</param>
        /// <returns>jwt token</returns>
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

        /// <summary>
        /// Gets the GitHub access token
        /// </summary>
        /// <param name="appId">GitHub app id</param>
        /// <param name="installationId">app installation id</param>
        /// <param name="jwtToken">jwt token</param>
        /// <returns>GitHub access token</returns>
        private static async Task<string> GetInstallationAccessToken(string installationId, string jwtToken)
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

        /// <summary>
        /// Handles the excpetion
        /// </summary>
        /// <param name="errorMessage">Error Message</param>
        /// <param name="ex">Excpetion</param>
        private void HandleException(string errorMessage, Exception ex)
        {
            Console.WriteLine($"{errorMessage}. Error message: {ex.Message}. Stack trace: {ex.StackTrace}");
        }

        /// <summary>
        /// Gets the pull request number.
        /// </summary>
        /// <returns>Pull request number.</returns>
        public int GetPullRequestNumber()
        {
            if (_prNumber == null)
            {
                int.TryParse(Environment.GetEnvironmentVariable("PRNUM"), out int prNumber);
                _prNumber = prNumber;
                // Uncomment below for debugging with a PR
                //_prNumber = 9476;
            }
            return _prNumber.GetValueOrDefault();
        }


        public static bool IsForkRepo()
        {
            if (bool.TryParse(Environment.GetEnvironmentVariable("SYSTEM_PULLREQUEST_ISFORK"), out bool isForkRepo))
            {
                return isForkRepo;
            }
            else
            {
                Console.WriteLine("Unbale to retrieve the value from the env variable SYSTEM_PULLREQUEST_ISFORK");
                return false;
            }
        }

    }

}
