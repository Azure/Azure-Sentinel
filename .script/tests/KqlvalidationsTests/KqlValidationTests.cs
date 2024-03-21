using System.Collections.Generic;
using Microsoft.Azure.Sentinel.KustoServices.Contract;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using YamlDotNet.Serialization;
using Microsoft.Azure.Sentinel.KustoServices.Implementation;
using Kqlvalidations.Tests.FunctionSchemasLoaders;
using System;
using Newtonsoft.Json;
using Octokit;

namespace Kqlvalidations.Tests
{
    public class KqlValidationTests
    {
        private readonly IKqlQueryAnalyzer _queryValidator;
        private const int TestFolderDepth = 3;
        private const string UserMessageTemplate = "Template Id:{0} is valid but it is in the skipped validation templates. Please remove it from the templates that are skipped since it is valid.";
        private const int TestFolderDepthForSolutionParsers = 6;

        public KqlValidationTests()
        {
            _queryValidator = new KqlQueryAnalyzerBuilder()
               .WithSentinelDefaultTablesAndFunctionsSchemas()
               .WithCustomTableSchemasLoader(new CustomJsonDirectoryTablesLoader(Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "CustomTables")))
               .WithCustomFunctionSchemasLoader(new CustomJsonDirectoryFunctionsLoader(Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "CustomFunctions")))
               .WithCustomFunctionSchemasLoader(new ParsersCustomJsonDirectoryFunctionsLoader(Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "CustomFunctions")))
               .WithCustomFunctionSchemasLoader(new CommonFunctionsLoader())
               .Build();
        }


        [Theory]
        [ClassData(typeof(DataConnectorFilesTestData))]
        public void Validate_DataConnectors_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.json")
            {
                Assert.True(true);
                return;
            }
            var dataConnector = ReadAndDeserializeDataConnectorJson(encodedFilePath);
            var id = (string)dataConnector.Id;
            //we ignore known issues
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }
            foreach (var connectivityCriteria in dataConnector.ConnectivityCriterias)
            {
                //check only if connectivity criteria type is eqaul to "IsConnectedQuery"
                if (connectivityCriteria.Type.Equals("IsConnectedQuery", StringComparison.OrdinalIgnoreCase))
                {
                    foreach (var queryStr in connectivityCriteria.Value)
                    {
                        ValidateKql(id, queryStr);
                    }
                }
            }

            foreach (var sampleQuery in dataConnector.SampleQueries)
            {
                ValidateKql(id, sampleQuery.Query);
            }

            foreach (var graphQuery in dataConnector.GraphQueries)
            {
                ValidateKql(id, graphQuery.BaseQuery);
            }

            foreach (var datatype in dataConnector.DataTypes)
            {
                ValidateKql(id, datatype.LastDataReceivedQuery);
            }
        }

        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(HuntingQueriesYamlFilesTestData))]
        public void Validate_HuntingQueries_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["id"];

            //we ignore known issues. We also ignore templates that are not in the skipped templates list.
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            var queryStr = (string)res["query"];
            ValidateKql(id, queryStr);
            ValidateKqlForBestPractices(queryStr, fileName);
            ValidateKqlForLatestTIData(id, queryStr);
        }

        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["id"];

            //we ignore known issues
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            var queryStr = (string)res["query"];
            ValidateKql(id, queryStr);
            ValidateKqlForBestPractices(queryStr,fileName);
            ValidateKqlForLatestTIData(id, queryStr);
        }

        /// <summary>
        /// Validates the KQL for the best practices
        /// </summary>
        /// <param name="queryStr">Query string</param>
        /// <param name="filename">KQL file name</param>
        private void ValidateKqlForBestPractices(string queryStr, string filename)
        {
            try
            {
                // Commenting temporarily for adding some additional functionality
                //if (!GitHubApiClient.IsForkRepo())
                //{
                //    var suggestions = KqlBestPracticesChecker.CheckBestPractices(queryStr, filename);
                //    if (!string.IsNullOrEmpty(suggestions))
                //    {
                //        var gitHubApiClient = GitHubApiClient.Create();
                //        gitHubApiClient.AddPRComment(suggestions);
                //    } 
                //}
            }
            catch (Exception ex)
            {
                // Log the exception or handle it appropriately
                Console.WriteLine($"Error occurred while validating KQL for best practices. Error message: {ex.Message}. Stack trace: {ex.StackTrace}");
            }
        }



        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(HuntingQueriesYamlFilesTestData))]
        public void Validate_HuntingQueries_SkippedTemplatesDoNotHaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["id"];

            //Templates that are in the skipped templates should not pass the validation (if they pass, why skip?)
            if (ShouldSkipTemplateValidation(id) && res.ContainsKey("query"))
            {
                var queryStr = (string)res["query"];
                bool validationRes = _queryValidator.ValidateSyntax(queryStr).IsValid && ValidateKqlForLatestTI(queryStr);
                Assert.False(validationRes, string.Format(UserMessageTemplate, id));
            }

        }

        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(DetectionsYamlFilesTestData))]
        public void Validate_DetectionQueries_SkippedTemplatesDoNotHaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["id"];

            //Templates that are in the skipped templates should not pass the validation (if they pass, why skip?)
            if (ShouldSkipTemplateValidation(id) && res.ContainsKey("query"))
            {
                var queryStr = (string)res["query"];
                bool validationRes = _queryValidator.ValidateSyntax(queryStr).IsValid && ValidateKqlForLatestTI(queryStr);
                Assert.False(validationRes, string.Format(UserMessageTemplate, id));
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

        [Theory]
        [ClassData(typeof(ExplorationQueriesYamlFilesTestData))]
        public void Validate_ExplorationQueries_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["Id"];

            //we ignore known issues
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            var queryStr = (string)res["query"];
            ValidateKql(id, queryStr);
            ValidateKqlForBestPractices(queryStr, fileName);
        }

        [Theory]
        [ClassData(typeof(ExplorationQueriesYamlFilesTestData))]
        public void Validate_ExplorationQueries_SkippedTemplatesDoNotHaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["Id"];

            //Templates that are in the skipped templates should not pass the validation (if they pass, why skip?)
            if (ShouldSkipTemplateValidation(id) && res.ContainsKey("query"))
            {
                var queryStr = (string)res["query"];
                var validationRes = _queryValidator.ValidateSyntax(queryStr);
                Assert.False(validationRes.IsValid, string.Format(UserMessageTemplate, id));
            }

        }

        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(ParsersYamlFilesTestData))]
        public void Validate_ParsersFunctions_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            Dictionary<object, object> yaml = ReadAndDeserializeYaml(encodedFilePath);
            var queryParamsAsLetStatements = GenerateFunctionParametersAsLetStatements(yaml);

            //Ignore known issues
            yaml.TryGetValue("Id", out object id);
            if (id != null && ShouldSkipTemplateValidation((string)yaml["Id"]))
            {
                return;
            }

            var queryStr = queryParamsAsLetStatements + (string)yaml["ParserQuery"];
            var parserName = (string)yaml["ParserName"];
            ValidateKql(parserName, queryStr, false);
            ValidateKqlForBestPractices(queryStr, fileName);
        }

        // We pass File name to test because in the result file we want to show an informative name for the test
        [Theory]
        [ClassData(typeof(CommonFunctionsYamlFilesTestData))]
        public void Validate_CommonFunctions_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            Dictionary<object, object> yaml = ReadAndDeserializeYaml(encodedFilePath);
            var queryParamsAsLetStatements = GenerateFunctionParametersAsLetStatements(yaml, "FunctionParams");

            //Ignore known issues
            yaml.TryGetValue("Id", out object id);
            if (id != null && ShouldSkipTemplateValidation((string)id))
            {
                return;
            }

            var queryStr = queryParamsAsLetStatements + (string)yaml["FunctionQuery"];
            var parserName = (string)yaml["EquivalentBuiltInFunction"];
            ValidateKql(parserName, queryStr, false);
            ValidateKqlForBestPractices(queryStr, fileName);
        }


        [Theory]
        [ClassData(typeof(SolutionParsersYamlFilesTestData))]
        public void Validate_SolutionParsersFunctions_HaveValidKql(string fileName, string encodedFilePath)
        {
            if (fileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }
            Dictionary<object, object> yaml = ReadAndDeserializeYaml(encodedFilePath);
            var queryParamsAsLetStatements = GenerateFunctionParametersAsLetStatements(yaml, "FunctionParams");

            //Ignore known issues
            yaml.TryGetValue("id", out object id);
            if (id != null && ShouldSkipTemplateValidation((string)yaml["id"]))
            {
                return;
            }

            var queryStr = queryParamsAsLetStatements + (string)yaml["FunctionQuery"];
            var parserName = (string)yaml["FunctionName"];
            ValidateKql(id.ToString(), queryStr, false);
            ValidateKqlForBestPractices(queryStr, fileName);
        }

        //Will enable this test case once all txt files removed from the parsers folders
        //[Fact]
        //public void Validate_AllSolutionParsersFoldersContainsYamlsORMarkdowns()
        //{
        //    var basePath = Utils.GetTestDirectory(TestFolderDepthForSolutionParsers);
        //    var solutionDirectories = Path.Combine(basePath, "Solutions");
        //    var parserFolders = Directory.GetDirectories(solutionDirectories, "Parsers", SearchOption.AllDirectories);

        //    var allNonYamlMdFiles = parserFolders
        //        .SelectMany(parserFolder => Directory.GetFiles(parserFolder, "*", SearchOption.AllDirectories))
        //        .Where(file => !file.EndsWith(".yaml", StringComparison.OrdinalIgnoreCase) && !file.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
        //        .ToList();

        //    Assert.True(!allNonYamlMdFiles.Any(), $"All files under Parsers folders are supposed to have .yaml or .md extension");
        //}

        [Fact]
        public void Validate_AllSolutionParsersFoldersContainsYamlsORMarkdowns()
        {
            var gitHubApiClient = GitHubApiClient.Create();

            IReadOnlyList<PullRequestFile> prFiles = gitHubApiClient.GetPullRequestFiles();

            if (prFiles.Count == 0)
            {
                // No pull request files found, fail the test with an appropriate message
                Assert.True(false, "No pull request files found. Unable to perform validation.");
                return;
            }

            // Define constants for readability
            const string parsersFolder = "Parsers";
            const string parserFolder = "Parser";
            const string removedStatus = "removed";

            var basePath = Utils.GetTestDirectory(TestFolderDepthForSolutionParsers);
            var solutionDirectories = Path.Combine(basePath, "Solutions");
            var parserPaths = Directory.GetDirectories(solutionDirectories, parsersFolder, SearchOption.AllDirectories).ToList();
            parserPaths.AddRange(Directory.GetDirectories(solutionDirectories, parserFolder, SearchOption.AllDirectories).ToList());

            var allowedExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { ".yaml", ".md" };

            var filteredFiles = prFiles
                .Where(file =>
                    parserPaths.Any(parserPath => Path.Combine(basePath, file.FileName.Replace('/', Path.DirectorySeparatorChar)).StartsWith(parserPath, StringComparison.OrdinalIgnoreCase)) &&
                    file.Status != removedStatus &&
                    !allowedExtensions.Contains(Path.GetExtension(file.FileName)))
                .ToList();

            // Assert that there are no disallowed extensions
            Assert.False(filteredFiles.Any(), $"Files with disallowed extensions found: {string.Join(", ", filteredFiles.Select(file => file.FileName))}, Only {string.Join(", ", allowedExtensions)} extensions are allowed under Solution/Parsers folder.");
        }


        /// <summary>
        /// Validates the KQL query for the latest Threat Intelligence data.
        /// </summary>
        /// <param name="id">template id</param>
        /// <param name="queryStr">query string</param>
        private void ValidateKqlForLatestTIData(string id, string queryStr)
        {
            bool queryMatch = ValidateKqlForLatestTI(queryStr);
            Assert.True(
                queryMatch,
                queryMatch
                   ? string.Empty
    : @$"Template Id: {id} is not valid 
        Errors: Content needs to use the latest Threat Intelligence data. Sample queries to get the latest Threat Intelligence data:
        ThreatIntelligenceIndicator
        | where TimeGenerated >= ago(ioc_lookBack)
        | summarize LatestIndicatorTime = arg_max(TimeGenerated, *) by IndicatorId
        | where Active == true and ExpirationDateTime > now()

        or

        ThreatIntelligenceIndicator
        | where TimeGenerated >= ago(ioc_lookBack)
        | summarize LatestIndicatorTime = arg_max(TimeGenerated, *) by IndicatorId
        | where ExpirationDateTime > now() and Active == true");
        }

        /// <summary>
        /// Validates the KQL query for the latest Threat Intelligence data.
        /// </summary>
        /// <param name="queryStr">query string</param>
        /// <returns>returns true if query is valid</returns>
        private bool ValidateKqlForLatestTI(string queryStr)
        {
            //Condition to check below logic only when queryStr it contains "ThreatIntelligenceIndicator" followed by "|"
            string tiTablepattern = @"ThreatIntelligenceIndicator\s*\|\s*";
            bool match = Regex.IsMatch(queryStr, tiTablepattern);
            if (match)
            {
                string queryPattern = @"ThreatIntelligenceIndicator\s*\|\s*where\s*TimeGenerated\s*>=\s*ago\(\w+\).*|\s*summarize\s*LatestIndicatorTime\s*=\s*arg_max\(TimeGenerated,\s*\*\)\s*by\s*IndicatorId\s*\|\s*where\s*(?:ExpirationDateTime\s*>\s*now\(\)\s*and\s*Active\s*==\s*true|Active\s*==\s*true\s*and\s*ExpirationDateTime\s*>\s*now\(\))";
                return Regex.IsMatch(queryStr, queryPattern, RegexOptions.Singleline);
            }
            return true;
        }

        private void ValidateKql(string id, string queryStr, bool ignoreNoTabularExpressionError = true)
        {

            // The KQL validation ignores no tabular expression error. For instance, "let x = table;" is considered a valid query.
            // Add "| count" at the end of the query, to fail queries without tabular expressions.
            if (!ignoreNoTabularExpressionError)
            {
                queryStr += " | count";
            }

            var validationResult = _queryValidator.ValidateSyntax(queryStr);
            var firstErrorLocation = (Line: 0, Col: 0);
            if (!validationResult.IsValid)
            {
                firstErrorLocation = GetLocationInQuery(queryStr, validationResult.Diagnostics.First(d => d.Severity == "Error").Start);
            }

            var listOfDiagnostics = validationResult.Diagnostics;

            bool isQueryValid = !(from p in listOfDiagnostics
                                  where !p.Message.Contains("_GetWatchlist") //We do not validate the getWatchList, since the result schema is not known
                                  select p).Any();


            Assert.True(
                isQueryValid,
                isQueryValid
                    ? string.Empty
                    : @$"Template Id: {id} is not valid in Line: {firstErrorLocation.Line} col: {firstErrorLocation.Col}
                    Errors: {validationResult.Diagnostics.Select(d => d.ToString()).ToList().Aggregate((s1, s2) => s1 + "," + s2)}");
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
                .Where(template => 
template.id
 == templateId)
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

        /// <summary>
        /// Generate a string of function parameters as let statements.
        /// </summary>
        /// <param name="yaml">The parser's yaml file</param>
        /// <returns>The function parameters as let statements</returns>
        private string GenerateFunctionParametersAsLetStatements(Dictionary<object, object> yaml, string paramsKey = "ParserParams")
        {
            if (yaml.TryGetValue(paramsKey, out object parserParamsObject))
            {
                var parserParams = (List<object>)parserParamsObject;
                return string.Join(Environment.NewLine, parserParams.Select(GenerateParamaterAsLetStatement).ToList());
            }
            return "";
        }

        /// <summary>
        /// Convert function parameter to a let statement with the format 'let <parameterName>= <defaultValue>;
        /// </summary>
        /// <param name="parameter">A function parameter as an object</param>
        /// <returns>A function parameter as a let statement</returns>
        private string GenerateParamaterAsLetStatement(object parameter)
        {
            var dictionary = (IReadOnlyDictionary<object, object>)parameter;
            string name = (string)dictionary["Name"];
            string type = (string)dictionary["Type"];
            string defaultValue = ((string)dictionary.GetValueOrDefault("Default")) ?? TypesDatabase.TypeToDefaultValueMapping.GetValueOrDefault(type);
            return $"let {name}= {(type == "string" ? $"'{defaultValue}'" : defaultValue)};";
        }

        private DataConnectorSchema ReadAndDeserializeDataConnectorJson(string encodedFilePath)
        {
            var jsonString = File.ReadAllText(Utils.DecodeBase64(encodedFilePath));
            DataConnectorSchema dataConnectorObject = JsonConvert.DeserializeObject<DataConnectorSchema>(jsonString);
            return dataConnectorObject;
        }
    }

}

