using System.Collections.Generic;
using System.IO;
using System.Linq;
using Octokit;

namespace Kqlvalidations.Tests
{
    public abstract class YamlFilesLoader
    {
        protected const int TestFolderDepth = 6;

        protected abstract List<string> GetDirectoryPaths();

        public List<string> GetFilesNames()
        {
            int prNumber = 0;
            int.TryParse(System.Environment.GetEnvironmentVariable("PRNUM"), out prNumber);
            if (prNumber == 0)
            {
                prNumber = 8414;
            }
            var client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            foreach (var file in prFiles)
            {
                var modifiedFile = Path.Combine(basePath, file.FileName);
                prFilesListModified.Add(modifiedFile);
                //prFilesListModified.Add(modifiedFile.Replace("/", "\\"));
            }

            var validFiles = GetDirectoryPaths()
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                .Where(file => prFilesListModified.Any(prFile => file.Contains(prFile)))
                .ToList();

            if (validFiles.Count == 0)
            {
                validFiles.Add("NoFile.yaml");
            }

            return validFiles;
        }

    }
}