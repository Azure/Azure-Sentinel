using Octokit;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Kqlvalidations.Tests
{
    public abstract class YamlFilesLoader
    {
        protected const int TestFolderDepth = 6;

        protected abstract List<string> GetDirectoryPaths();
        
        public List<string> GetFilesNames()
        {
            int prNumber = int.Parse(System.Environment.GetEnvironmentVariable("PRNUM"));
            var client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            foreach (var file in prFiles)
            {
                var modifiedFile = Path.Combine(basePath, file.FileName);
                prFilesListModified.Add(modifiedFile.Replace("/", "\\"));
                Console.WriteLine(modifiedFile.Replace("/", "\\"));
            }

            return GetDirectoryPaths()
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                .Where(file => prFilesListModified.Any(prFile => file.Contains(prFile)))
                .ToList();
        }
    }
}