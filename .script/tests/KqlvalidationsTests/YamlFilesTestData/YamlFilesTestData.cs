using Octokit;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http.Headers;
using ProductHeaderValue = Octokit.ProductHeaderValue;

namespace Kqlvalidations.Tests
{
    public class YamlFilesTestData : TheoryData<string, string>
    {
        protected const int TestFolderDepth = 6;
        public YamlFilesTestData(YamlFilesLoader yamlFilesLoader, List<string> fileNamesToIgnore = null)
        {
            var files = yamlFilesLoader.GetFilesNames();
            
            int prNumber = int.Parse(Environment.GetEnvironmentVariable("FOO"));

            //Get PR details using the PR number from GitHub API
            var client = new GitHubClient(new ProductHeaderValue("MyAmazingApp"));
            //var pr = client.PullRequest.Get("Azure-Sentinel", "Azure-Sentinel", prNumber).Result;
            var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
            var prFilesListModified = new List<string>();
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            foreach (var file in prFiles)
            {
                var modifiedFile = file.FileName.Replace("/", "\\");
                modifiedFile =Path.Combine(basePath, modifiedFile);
                prFilesListModified.Add(modifiedFile);
            }

            //filter files with pfFilesList
            var filteredFiles = files.Where(file => prFilesListModified.Any(prFile => file.Contains(prFile))).ToList();
            filteredFiles.ForEach(filePath =>
            {
                if (!fileNamesToIgnore?.Any(fileNameToIgnore => filePath.EndsWith(fileNameToIgnore)) ?? true)
                {
                    var fileName = Path.GetFileName(filePath);
                    Add(fileName, Utils.EncodeToBase64(filePath));
                }
            });
        }
    }
}
