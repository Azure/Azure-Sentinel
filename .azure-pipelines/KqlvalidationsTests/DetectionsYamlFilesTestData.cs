using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Kqlvalidations.Tests
{
    public class DetectionsYamlFilesTestData : TheoryData<string>
    {
        public DetectionsYamlFilesTestData()
        {
            var rootDir = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().CodeBase);
            var detectionPath = $"{rootDir}/../../../../../Detections".Replace(@"file:/", string.Empty);
            var files = Directory.GetFiles(detectionPath, "*.yaml", SearchOption.AllDirectories).ToList();
            files.ForEach(f => AddData(f));
        }
    }
}
