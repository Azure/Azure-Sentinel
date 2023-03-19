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
            int prNumber = 7574;// int.Parse(System.Environment.GetEnvironmentVariable("PRNUM"));
            var client = new GitHubClient(new ProductHeaderValue("MyAmazingApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            foreach (var file in prFiles)
            {
                var modifiedFile = file.FileName.Replace("/", "\\"); 
                string rootDirectory = Environment.GetEnvironmentVariable("ROOT_DIRECTORY");
                if (string.IsNullOrEmpty(rootDirectory))
                {
                    Console.WriteLine("Error: ROOT_DIRECTORY environment variable is not set.");
                    return null;
                }
                Console.WriteLine($"{rootDirectory} {modifiedFile}");
                modifiedFile = Path.Combine(rootDirectory, "Azure Sentinel", modifiedFile);
                prFilesListModified.Add(modifiedFile);
            }

            return GetDirectoryPaths()
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                .Where(file => prFilesListModified.Any(prFile => file.Contains(prFile)))
                .ToList();
        }
    }
}