using Microsoft.Azure.Sentinel.KustoServices.Contract;
using System;
using System.IO;
using System.Linq;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    public class KqlValidationTests
    {
        private readonly IKqlQueryValidator _queryValidator;
        public KqlValidationTests()
        {
            _queryValidator = new KqlQueryValidatorBuilder()
               .WithSentinelDefaultTableSchemas()
               //.WithCustomTableSchema(GetCustomLogsSchemas())
               .Build();
        }

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void validate_detectionqueries_succeed(string detectionsYamlFile)
        {
            var yaml = File.ReadAllText(detectionsYamlFile);
            var deserializer = new DeserializerBuilder().Build();
            var res = deserializer.Deserialize<dynamic>(yaml);
            string queryStr = res["query"];

            var validationRes = _queryValidator.ValidateSyntax(queryStr);

            Assert.True(validationRes.IsValid, validationRes.IsValid ? string.Empty : validationRes.Diagnostics.Select(d => d.Message).ToList().Aggregate((s1, s2) => s1 + "," + s2));
        }

    }
}
