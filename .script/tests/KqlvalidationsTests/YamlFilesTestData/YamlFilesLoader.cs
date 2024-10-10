using System;
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

        //declare load all files on optional parameter loadAllFiles

        public List<string> GetFilesNames(bool loadAllFiles = false)
        {
            var gitHubApiClient = GitHubApiClient.Create();

            if (loadAllFiles)
            {
                // Load all files without PR filter
                return GetAllFiles();
            }

            int prNumber = gitHubApiClient.GetPullRequestNumber();

            if (prNumber == 0)
            {
                Console.WriteLine("PR Number is not set. Running all tests");
                return GetAllFiles();
            }

            try
            {
                var prFiles = gitHubApiClient.GetPullRequestFiles();

                if (prFiles != null && prFiles.Count > 0)
                {
                    return GetValidFiles(prFiles);
                }
            }
            catch (Exception ex)
            {
                // Console.WriteLine the exception
                Console.WriteLine($"Error occurred: {ex.Message}. Stack trace: {ex.StackTrace}");
            }

            // If there are issues with PR files, return all files
            return GetAllFiles();
        }

        private List<string> GetAllFiles()
        {
            return GetDirectoryPaths()
                .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                .ToList();
        }

        private List<string> GetValidFiles(IReadOnlyList<PullRequestFile> prFiles)
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepth);
            var prFilesListModified = prFiles.Select(file => Path.Combine(basePath, file.FileName.Replace('/', Path.DirectorySeparatorChar))).ToList();

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