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
        private readonly IKqlQueryValidator _queryValidator;
        //TODO: read from configuration
        private readonly static IEnumerable<string> WhiteListTemplateIds = new string[] { "aac495a9-feb1-446d-b08e-a1164a539452","f948a32f-226c-4116-bddd-d95e91d97eb9", "39198934-62a0-4781-8416-a81265c03fd6", "3533f74c-9207-4047-96e2-0eb9383be587", "9fb57e58-3ed8-4b89-afcf-c8e786508b1c", "24f8c234-d1ff-40ec-8b73-96b17a3a9c1c", "d6491be0-ab2d-439d-95d6-ad8ea39277c5", "0914adab-90b5-47a3-a79f-7cdcac843aa7", "06a9b845-6a95-4432-a78b-83919b28c375", "57e56fc9-417a-4f41-a579-5475aea7b8ce", "155f40c6-610d-497d-85fc-3cf06ec13256", "f2dd4a3a-ebac-4994-9499-1a859938c947", "884be6e7-e568-418e-9c12-89229865ffde", "e27dd7e5-4367-4c40-a2b7-fcd7e7a8a508", "0558155e-4556-447e-9a22-828f2a7de06b", "34663177-8abf-4db1-b0a4-5683ab273f44", "a9956d3a-07a9-44a6-a279-081a85020cae","04384937-e927-4595-8f3c-89ff58ed231f" };
        private static readonly string DetectionPath = DetectionsYamlFilesTestData.GetDetectionPath();
        public KqlValidationTests()
        {
            _queryValidator = new KqlQueryValidatorBuilder()
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
            if (WhiteListTemplateIds.Contains(id))
            {
                return;
            }
            var validationRes = _queryValidator.ValidateSyntax(queryStr);
            Assert.True(validationRes.IsValid, validationRes.IsValid ? string.Empty : validationRes.Diagnostics.Select(d => d.Message).ToList().Aggregate((s1, s2) => s1 + "," + s2));
        }
    }

}

