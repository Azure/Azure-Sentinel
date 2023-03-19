using Octokit;
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
            
            return GetDirectoryPaths().Aggregate(new List<string>(), (accumulator, directoryPath) =>
            {
                var files = Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories).ToList();
                return accumulator.Concat(files).ToList();
            });

            int prNumber = 7574;// int.Parse(System.Environment.GetEnvironmentVariable("PRNUM"));
            var client = new GitHubClient(new ProductHeaderValue("MyAmazingApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            foreach (var file in prFiles)
            {
                var modifiedFile = "/home/vsts/work/1/s/" + file.FileName;
                //var modifiedFile = "C:\\Azure Sentinel\\" + file.FileName;
                prFilesListModified.Add(modifiedFile.Replace("/", "\\"));
            }

            return GetDirectoryPaths()
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                .Where(file => prFilesListModified.Any(prFile => file.Contains(prFile)))
                .ToList();
        }
    }
}