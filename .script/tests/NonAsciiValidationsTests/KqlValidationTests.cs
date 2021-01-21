using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Xunit;

namespace Kqlvalidations.Tests
{
    public class NonAsciiValidationsTests
    {

        private static readonly string DetectionPath = DetectionsYamlFilesTestData.GetDetectionPath();

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionFile_HaveOnlyAsciiChars(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            var yaml = File.ReadAllText(detectionsYamlFile);
            var nonAsciiCharMatch = Regex.Match(yaml, @"[^\u0000-\u007F]+");
            Assert.False(nonAsciiCharMatch.Success, $"include the non ascii char:{nonAsciiCharMatch.Value} string index:{nonAsciiCharMatch.Index}");
        }
    }

}

