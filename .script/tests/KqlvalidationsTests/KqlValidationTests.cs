using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
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

            //we ignore known issues (in progress)
            if (TemplatesToSkipValidationReader.WhiteListTemplateIds.Contains(id))
            {
                return;
            }
            var validationRes = _queryValidator.ValidateSyntax(queryStr);
            Assert.True(validationRes.IsValid, validationRes.IsValid ? string.Empty : $"Template Id:{id} is not valid Errors:{validationRes.Diagnostics.Select(d => d.ToString()).ToList().Aggregate((s1, s2) => s1 + "," + s2)}");
        }
    }

}

