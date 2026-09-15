using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;

namespace Kqlvalidations.Tests
{
    public class DetectionsYamlFilesTestData : TheoryData<string>
    {
        public DetectionsYamlFilesTestData()
        {
            List<string> detectionPaths = GetDetectionPaths();
            var files = GetDetectionFiles(detectionPaths);
            files.ForEach(f => AddData(Path.GetFileName(f)));
        }

        public static List<string> GetDetectionPaths()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            List<string> dirPaths = new List<string>() { "Detections", "Solutions" };
            var testFolderDepth = 6;
            List<string> detectionPaths = new List<string>();
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }

            foreach (var dirName in dirPaths)
            {
                detectionPaths.Add(Path.Combine(rootDir.FullName, dirName));
            }

            return detectionPaths;
        }

        public static string GetRootPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            var testFolderDepth = 6;
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            return rootDir.FullName;
        }

        public static string GetSkipTemplatesPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            var testFolderDepth = 3;
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            return rootDir.FullName;
        }

        private static string GetAssemblyDirectory()
        {
            string codeBase = Assembly.GetExecutingAssembly().CodeBase;
            UriBuilder uri = new UriBuilder(codeBase);
            string path = Uri.UnescapeDataString(uri.Path);
            return Path.GetDirectoryName(path);
        }

        private static List<string> GetDetectionFiles(List<string> detectionPaths)
        {
            int prNumber = 0;
            int.TryParse(Environment.GetEnvironmentVariable("PRNUM"), out prNumber);
            //assign pr number to debug with a pr
            //prNumber=8414;
            var files = Directory.GetFiles(detectionPaths[0], "*.yaml", SearchOption.AllDirectories)
                .Concat(Directory.GetFiles(detectionPaths[1], "*.yaml", SearchOption.AllDirectories)
                .Where(s => s.Contains("Analytic Rules")));

            if (prNumber != 0)
            {
                try
                {
                    var basePath = GetRootPath();
                    var prFilesListModified = GetPullRequestModifiedFiles(basePath);

                    files = files.Where(file => prFilesListModified.Contains(Path.GetFullPath(file)));
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Error occured while getting the files from PR. Error message: " + ex.Message + " Stack trace: " + ex.StackTrace);
                }
            }

            var fileList = files.ToList();

            if (fileList.Count == 0)
            {
                fileList.Add("NoFile.yaml");
            }

            return fileList;
        }

        private static HashSet<string> GetPullRequestModifiedFiles(string basePath)
        {
            var processStartInfo = new ProcessStartInfo("git", "diff --name-only HEAD^1 HEAD")
            {
                WorkingDirectory = basePath,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false
            };

            using (var process = Process.Start(processStartInfo))
            {
                var output = process.StandardOutput.ReadToEnd();
                var error = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (process.ExitCode != 0)
                {
                    throw new Exception($"git diff failed with exit code {process.ExitCode}: {error}");
                }

                return output
                    .Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(fileName => Path.GetFullPath(Path.Join(basePath, fileName.Replace('/', Path.DirectorySeparatorChar))))
                    .ToHashSet();
            }
        }

    }
}