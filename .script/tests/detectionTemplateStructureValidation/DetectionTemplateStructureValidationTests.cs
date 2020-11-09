using System.IO;
using System.Linq;
using FluentAssertions;
using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    public class DetectionTemplateStructureValidationTests
    {
        private static readonly string DetectionPath = DetectionsYamlFilesTestData.GetDetectionPath();

        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionTemplates_HaveValidTemplateStructure(string detectionsYamlFileName)
        {
            var detectionsYamlFile = Directory.GetFiles(DetectionPath, detectionsYamlFileName, SearchOption.AllDirectories).Single();
            var yaml = File.ReadAllText(detectionsYamlFile);

            //we ignore known issues (in progress)
            foreach (var templateToSkip in TemplatesToSkipValidationReader.WhiteListTemplateIds)
            {
                if (yaml.Contains(templateToSkip) || detectionsYamlFile.Contains(templateToSkip))
                {
                    return;
                }
            }

            var jObj = JObject.Parse(ConvertYamlToJson(yaml));

            var exception = Record.Exception(() => jObj.ToObject<ScheduledTemplateInternalModel>());
            exception.Should().BeNull();
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