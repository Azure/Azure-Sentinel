using System;
using System.IO;
using System.Linq;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;
using Microsoft.Azure.Sentinel.KustoServices.Contract;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
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
            if (TemplatesToSkipValidationReader.WhiteListTemplateIds_MalformedQueries.Contains(id))
            {
                return;
            }
            var validationRes = _queryValidator.ValidateSyntax(queryStr);
            Assert.True(validationRes.IsValid, validationRes.IsValid ? string.Empty : $"Template Id:{id} is not valid Errors:{validationRes.Diagnostics.Select(d => d.ToString()).ToList().Aggregate((s1, s2) => s1 + "," + s2)}");
        }

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_HaveValidTemplateStructure(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            var yaml = File.ReadAllText(detectionsYamlFile);

            //we ignore known issues (in progress)
            foreach (var templateToSkip in TemplatesToSkipValidationReader.WhiteListTemplateIds_MalformedTemplateStructure)
            {
                if (yaml.Contains(templateToSkip) || detectionsYamlFile.Contains(templateToSkip))
                {
                    return;
                }
            }

            var jObj = JObject.Parse(ConvertYamlToJson(yaml));
            jObj.Add("kind", "Scheduled");
            jObj.Add("lastUpdatedDateUTC", DateTime.UtcNow);
            jObj.Add("createdDateUTC", DateTime.UtcNow);

            jObj.ToObject<ScheduledTemplateInternalModel>();
        }

        public static string ConvertYamlToJson(string yaml)
        {
            var deserializer = new Deserializer();
            var yamlObject = deserializer.Deserialize<object>(yaml);

            using (var jsonObject = new StringWriter())
            {
                var serializer = new JsonSerializer();
                serializer.Serialize(jsonObject, yamlObject);
                return jsonObject.ToString();
            }
        }
    }
}