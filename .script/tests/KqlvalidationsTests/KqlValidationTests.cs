using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Newtonsoft.Json;
using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    public class KqlValidationTests
    {
        private readonly IKqlQueryAnalyzer _queryValidator;
        private static readonly string DetectionPath = DetectionsYamlFilesTestData.GetDetectionPath();
        public KqlValidationTests()
        {
            _queryValidator = new KqlQueryAnalyzerBuilder()
               .WithSentinelDefaultTableSchemas()
               .WithCustomTableSchemasLoader(new CustomTablesSchemasLoader())
               .Build();
        }

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_HaveValidKql(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            var yaml = File.ReadAllText(detectionsYamlFile);
            var deserializer = new DeserializerBuilder().Build();
            var res = deserializer.Deserialize<dynamic>(yaml);
            string queryStr = res["query"];
            string id = res["id"];

            //we ignore known issues
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            var validationRes = _queryValidator.ValidateSyntax(queryStr);
            var firstErrorLocation = (Line: 0, Col: 0);
            if (!validationRes.IsValid)
            {
                firstErrorLocation =  GetLocationInQuery(queryStr, validationRes.Diagnostics.First(d => d.Severity == "Error").Start);
            }
            Assert.True(validationRes.IsValid, validationRes.IsValid ? string.Empty : $"Template Id:{id} is not valid in Line:{firstErrorLocation.Line} col:{firstErrorLocation.Col} Errors:{validationRes.Diagnostics.Select(d => d.ToString()).ToList().Aggregate((s1, s2) => s1 + "," + s2)}");
        }
        
        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_SkippedTemplatesDoNotHaveValidKql(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            var yaml = File.ReadAllText(detectionsYamlFile);
            var deserializer = new DeserializerBuilder().Build();
            var res = deserializer.Deserialize<dynamic>(yaml);
            string queryStr = res["query"];
            string id = res["id"];

            //Templates that are in the skipped templates should not pass the validateion (if they pass, why skip?)
            if (ShouldSkipTemplateValidation(id))
            {
                var validationRes = _queryValidator.ValidateSyntax(queryStr);
                Assert.False(validationRes.IsValid, $"Template Id:{id} is valid but it is in the skipped validation templates. Please remove it from the templates that are skipped since it is valid.");
            }

            else
            {
                return;
            }
            
        }

        private bool ShouldSkipTemplateValidation(string templateId)
        {
            return TemplatesToSkipValidationReader.WhiteListTemplates
                .Where(template => template.id == templateId)
                .Where(template => !string.IsNullOrWhiteSpace(template.validationFailReason))
                .Where(template => !string.IsNullOrWhiteSpace(template.templateName))
                .Any();
        }

        private (int Line, int Col) GetLocationInQuery(string queryStr, int pos)
        {
            var lines = Regex.Split(queryStr, "\n");
            var curlineIndex = 0;
            var curPos = 0;

            while (lines.Length > curlineIndex && pos > curPos + lines[curlineIndex].Length + 1)
            {
                curPos += lines[curlineIndex].Length + 1;
                curlineIndex++;
            }
            var col = (pos - curPos + 1);
            return (curlineIndex + 1, col);
        }
    }

}

