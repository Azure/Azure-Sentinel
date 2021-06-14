using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace NonAsciiValidations.Tests
{
    public class NonAsciiValidationsTests
    {
        [Theory]
        [ClassData(typeof(HuntingQueriesYamlFilesTestData))]
        public void Validate_Hunting_HaveOnlyAsciiChars(string huntingYamlFileName,string yamlFullPath)
        {
            ValidateOnlyAscii(yamlFullPath, huntingYamlFileName);
        }

        [Theory]
        [ClassData(typeof(ParsersYamlFilesTestData))]
        public void Validate_Parsers_HaveOnlyAsciiChars(string parserYamlFileName, string yamlFullPath)
        {
            ValidateOnlyAscii(yamlFullPath, parserYamlFileName);
        }

        [Theory]
        [ClassData(typeof(ExplorationQueriesYamlFilesTestData))]
        public void Validate_ExplorationQueries_HaveOnlyAsciiChars(string explorationQueryYamlFileName, string yamlFullPath)
        {
            ValidateOnlyAscii(yamlFullPath, explorationQueryYamlFileName);
        }

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionFile_HaveOnlyAsciiChars(string detectionsYamlFileName, string yamlFullPath)
        {
            ValidateOnlyAscii(yamlFullPath, detectionsYamlFileName);
        }

        private void ValidateOnlyAscii(string yamlFilePath, string yamlFileName)
        {
            var yaml = File.ReadAllText(yamlFilePath);
            var nonAsciiCharMatch = Regex.Match(yaml, @"[^\u0000-\u007F]+");
            Assert.False(nonAsciiCharMatch.Success, $"${yamlFileName} includes the non ascii char:{nonAsciiCharMatch.Value} string index:{nonAsciiCharMatch.Index}");
        }
    }

}

