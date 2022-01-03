using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

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
            List<string> dirPaths = new List<string>() { "Detections", "Solutions"};
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
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

        public static string GetCustomTablesPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            var testFolderDepth = 3;
            for (int i = 0; i < testFolderDepth; i++)
            {
                rootDir = rootDir.Parent;
            }
            var detectionPath = Path.Combine(rootDir.FullName, "CustomTables");
            return detectionPath;
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
            var files = Directory.GetFiles(detectionPaths[0], "*.yaml", SearchOption.AllDirectories).ToList();
            files.AddRange(Directory.GetFiles(detectionPaths[1], "*.yaml", SearchOption.AllDirectories).ToList().Where(s => s.Contains("Analytic Rules")));

            return files;
        }
    }
}
