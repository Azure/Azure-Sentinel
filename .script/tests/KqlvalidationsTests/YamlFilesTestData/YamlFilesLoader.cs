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

        public List<string> GetFilesNames(bool loadAllFiles=false)
        {
            if(loadAllFiles)
            {
                return GetDirectoryPaths()
                    .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                    .ToList();
            }
            int prNumber = 0;
            int.TryParse(System.Environment.GetEnvironmentVariable("PRNUM"), out prNumber);
            //assign pr number to debug with a pr
            //prNumber=8595;
            if (prNumber == 0)
            {
                Console.WriteLine("PR Number is not set. Running all tests");
                return GetDirectoryPaths()
                    .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                    .ToList();
            }
            else
            {
                try
                {
                    var client = new GitHubClient(new ProductHeaderValue("MicrosoftSentinelValidationApp"));
                    var prFiles = client.PullRequest.Files("Azure", "Azure-Sentinel", prNumber).Result;
                    var prFilesListModified = new List<string>();
                    var basePath = Utils.GetTestDirectory(TestFolderDepth);
                    foreach (var file in prFiles)
                    {
                        var modifiedFile = Path.Combine(basePath, file.FileName.Replace('/', Path.DirectorySeparatorChar));
                        prFilesListModified.Add(modifiedFile);
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
                catch (Exception ex)
                {
                    // Exception occurred, return all files without filtering if there is any error in fetching PR Files
                    Console.WriteLine("Error occured while getting the files from PR. Error message: " + ex.Message + " Stack trace: " + ex.StackTrace);
                    return GetDirectoryPaths()
                        .SelectMany(directoryPath => Directory.GetFiles(directoryPath, "*.yaml", SearchOption.AllDirectories))
                        .ToList();
                }
            }
        }






    }
}