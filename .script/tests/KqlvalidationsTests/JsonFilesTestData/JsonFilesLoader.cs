using Octokit;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public abstract class JsonFilesLoader
    {
        protected const int TestFolderDepth = 6;

        protected abstract List<string> GetDirectoryPaths();

        public virtual List<string> GetFilesNames()
        {
            int prNumber = int.Parse(System.Environment.GetEnvironmentVariable("PRNUM"));
            var client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFileNames = prFiles.Select(file => file.FileName.Replace("/", "\\")).ToList();

            var directoryPaths = GetDirectoryPaths();

            if (directoryPaths == null)
            {
                return new List<string>();
            }

            return directoryPaths
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.json", SearchOption.AllDirectories))
                .Where(file => prFileNames.Any(prFile => file.Contains(prFile)))
                .ToList();
        }
    }
}