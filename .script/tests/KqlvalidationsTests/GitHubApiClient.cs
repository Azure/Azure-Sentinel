using Octokit;
using System;
using System.Collections.Generic;

namespace Kqlvalidations.Tests
{
    public sealed class GitHubApiClient
    {
        private static GitHubApiClient _instance;
        private readonly GitHubClient _client;

        private string _owner = "Azure";
        private string _repo = "Azure-Sentinel";
        private int? _prNumber;
        private IReadOnlyList<PullRequestFile> _cachedPullRequestFiles;

        private GitHubApiClient()
        {
            _client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
        }

        public static GitHubApiClient Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new GitHubApiClient();
                }
                return _instance;
            }
        }

        public void SetRepositoryDetails(string owner, string repo)
        {
            _owner = owner;
            _repo = repo;
        }

        public int GetPullRequestNumber()
        {
            if (_prNumber == null)
            {
                int.TryParse(Environment.GetEnvironmentVariable("PRNUM"), out int prNumber);
                _prNumber = prNumber;
                //uncomment below for debugging with a PR
                //_prNumber =8870;
            }

            return _prNumber.GetValueOrDefault();
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
                    // Handle the exception as needed
                    Console.WriteLine($"Error occurred while getting PR files. Error message: {ex.Message}. Stack trace: {ex.StackTrace}");
                    _cachedPullRequestFiles = new List<PullRequestFile>();
                }
            }

            return _cachedPullRequestFiles;
        }
    }
}
