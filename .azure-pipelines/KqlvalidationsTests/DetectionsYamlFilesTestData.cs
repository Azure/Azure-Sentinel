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
            string detectionPath = GetDetectionPath();
            var files = Directory.GetFiles(detectionPath, "*.yaml", SearchOption.AllDirectories).ToList();
            files.ForEach(f => AddData(Path.GetFileName(f)));
        }

        public static string GetDetectionPath()
        {
            var rootDir = Directory.CreateDirectory(GetAssemblyDirectory());
            for (int i = 0; i < 5; i++)
            {
                rootDir = rootDir.Parent;
            }
            var detectionPath = Path.Combine(rootDir.FullName, "Detections");
            return detectionPath;
        }

        private static string GetAssemblyDirectory()
        {
            string codeBase = Assembly.GetExecutingAssembly().CodeBase;
            UriBuilder uri = new UriBuilder(codeBase);
            string path = Uri.UnescapeDataString(uri.Path);
            return Path.GetDirectoryName(path);
        }
    }
}
