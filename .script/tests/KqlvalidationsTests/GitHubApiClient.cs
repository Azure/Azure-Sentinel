using Octokit;
using System;
using System.Collections.Generic;
using System.Linq;

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
            var accessToken = "";
            var credentials = new Credentials(accessToken);
            _client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            _client.Credentials = credentials;
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
                //_prNumber =9476;
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

        public void AddFileComment(string filePath, string comment)
        {
            try
            {
                int prNumber = GetPullRequestNumber();
                if (prNumber == 0)
                {
                    Console.WriteLine("PR number not available. Cannot add comment.");
                    return;
                }

                // Retrieve the list of files in the pull request
                var files = GetPullRequestFiles();

                // Find the file in the list of changed files
                var file = files[0];

                if (file != null)
                {
                    PullRequestReviewCommentCreate reviewCommentCreate = new PullRequestReviewCommentCreate(comment, file.Sha, file.FileName,0);

                    // Create a review comment for the specific file
                    var newComment = _client.PullRequest.ReviewComment.Create(_owner, _repo, prNumber, reviewCommentCreate).Result;
                }
                else
                {
                    Console.WriteLine($"File '{filePath}' not found in the list of changed files. Cannot add comment.");
                }
            }
            catch (Exception ex)
            {
                // Handle the exception as needed
                Console.WriteLine($"Error occurred while adding file comment. Error message: {ex.Message}. Stack trace: {ex.StackTrace}");
            }
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

                PullRequestReviewCreate pullRequestReviewCreate = new PullRequestReviewCreate();
                pullRequestReviewCreate.Body = comment;
                pullRequestReviewCreate.Event = PullRequestReviewEvent.Comment;

                //wrtie a comment to the PR saying files committed successfully
                var newComment = _client.PullRequest.Review.Create(_owner, _repo, prNumber, pullRequestReviewCreate).Result;
            }
            catch (Exception ex)
            {
                // Handle the exception as needed
                Console.WriteLine($"Error occurred while adding PR comment. Error message: {ex.Message}. Stack trace: {ex.StackTrace}");
            }
        }

    }
}
