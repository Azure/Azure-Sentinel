using System.Collections.Generic;
using Microsoft.Azure.Sentinel.KustoServices.Contract;
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
        public KqlValidationTests()
        {
            _queryValidator = new KqlQueryAnalyzerBuilder()
               .WithSentinelDefaultTableSchemas()
               .WithCustomTableSchemasLoader(new CustomTablesSchemasLoader())
               .Build();
        }

        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_HaveValidKql(string fileName, string encodedFilePath)
        {
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var queryStr =  (string) res["query"];
            var id = (string) res["id"];

            //we ignore known issues
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            ValidateKql(id, queryStr);
        }
        
        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_SkippedTemplatesDoNotHaveValidKql(string fileName, string encodedFilePath)
        {
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var queryStr =  (string) res["query"];
            var id = (string) res["id"];
        
            //Templates that are in the skipped templates should not pass the validation (if they pass, why skip?)
            if (ShouldSkipTemplateValidation(id))
            {
                var validationRes = _queryValidator.ValidateSyntax(queryStr);
                Assert.False(validationRes.IsValid, $"Template Id:{id} is valid but it is in the skipped validation templates. Please remove it from the templates that are skipped since it is valid.");
            }
        
        }
        
        // // We pass File name to test because in the result file we want to show an informative name for the test
        // [Theory]
        // [ClassData(typeof(InsightsYamlFilesTestData))]
        // public void Validate_InsightsQueries_HaveValidKqlBaseQuery(string fileName, string encodedFilePath)
        // {
        //     var res = ReadAndDeserializeYaml(encodedFilePath);
        //     var queryStr =  (string) res["BaseQuery"];
        //     
        //     ValidateKql(fileProp.FileName, queryStr);
        // }

        private void ValidateKql(string id, string queryStr)
        {
            var validationRes = _queryValidator.ValidateSyntax(queryStr);
            var firstErrorLocation = (Line: 0, Col: 0);
            if (!validationRes.IsValid)
            {
                firstErrorLocation = GetLocationInQuery(queryStr, validationRes.Diagnostics.First(d => d.Severity == "Error").Start);
            }

            Assert.True(validationRes.IsValid,
                validationRes.IsValid 
                    ? string.Empty 
                    : @$"Template Id: {id} is not valid in Line: {firstErrorLocation.Line} col: {firstErrorLocation.Col}
Errors: {validationRes.Diagnostics.Select(d => d.ToString()).ToList().Aggregate((s1, s2) => s1 + "," + s2)}");
        }

        private Dictionary<object, object> ReadAndDeserializeYaml(string encodedFilePath)
        {
        
            var yaml = File.ReadAllText(Utils.DecodeBase64(encodedFilePath));
            var deserializer = new DeserializerBuilder().Build();
            return deserializer.Deserialize<dynamic>(yaml);
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

