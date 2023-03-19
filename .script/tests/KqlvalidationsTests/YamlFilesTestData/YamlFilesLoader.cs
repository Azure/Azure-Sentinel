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
            var prNumber = int.Parse(System.Environment.GetEnvironmentVariable("PRNUM"));
            var client = new GitHubClient(new ProductHeaderValue("MyAmazingApp"));
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            foreach (var file in prFiles)
            {
                var modifiedFile = file.FileName.Replace("/", "\\");
                modifiedFile = "C:\\Azure Sentinel\\" + modifiedFile;
                prFilesListModified.Add(modifiedFile);
            }

            return GetDirectoryPaths()
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                .Where(file => prFilesListModified.Any(prFile => file.Contains(prFile)))
                .ToList();
        }
    }
}