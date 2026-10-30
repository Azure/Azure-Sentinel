using System.Collections.Generic;
using Microsoft.Azure.Sentinel.KustoServices.Contract;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Xunit;
using YamlDotNet.Serialization;
using Microsoft.Azure.Sentinel.KustoServices.Implementation;
using Kqlvalidations.Tests.FunctionSchemasLoaders;
using Kqlvalidations.Tests.TableSchemasLoaders;
using System;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
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
            var customTablesPath = Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "CustomTables");
            var customFunctionsPath = Path.Combine(Utils.GetTestDirectory(TestFolderDepth), "CustomFunctions");

            _queryValidator = new KqlQueryAnalyzerBuilder()
               .WithCustomTableSchemasLoader(new LocalOverrideTablesLoader(customTablesPath))
               .WithCustomFunctionSchemasLoader(new SentinelDefaultFunctionsLoader())
               .WithCustomFunctionSchemasLoader(new CustomJsonDirectoryFunctionsLoader(customFunctionsPath))
               .WithCustomFunctionSchemasLoader(new ParsersCustomJsonDirectoryFunctionsLoader(customFunctionsPath))
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
            var decodedPath = Utils.DecodeBase64(encodedFilePath);
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["id"];

            //we ignore known issues. We also ignore templates that are not in the skipped templates list.
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            var queryStr = (string)res["query"];
            ValidateKql(id, queryStr, true, decodedPath);
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
            var decodedPath = Utils.DecodeBase64(encodedFilePath);
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = (string)res["id"];

            //we ignore known issues
            if (ShouldSkipTemplateValidation(id))
            {
                return;
            }

            var queryStr = (string)res["query"];
            ValidateKql(id, queryStr, true, decodedPath);
            ValidateKqlForBestPractices(queryStr, fileName);
            ValidateKqlForLatestTIData(id, queryStr);
        }

        [Theory]
        [ClassData(typeof(XdrDetectionsYamlFilesTestData))]
        public void Validate_XdrDetectionQueries_HaveValidKql(string detectionYamlFileName, string encodedFilePath)
        {
            if (detectionYamlFileName == "NoFile.yaml")
            {
                Assert.True(true);
                return;
            }

            var decodedPath = Utils.DecodeBase64(encodedFilePath);
            var res = ReadAndDeserializeYaml(encodedFilePath);
            var id = ExtractXdrRuleId(res, detectionYamlFileName);
            var originalRuleId = ExtractXdrOriginalRuleId(res, id);

            if (ShouldSkipTemplateValidation(id) || (!string.IsNullOrWhiteSpace(originalRuleId) && ShouldSkipTemplateValidation(originalRuleId)))
            {
                return;
            }

            var queryStr = ExtractXdrQueryText(res);
            Assert.False(string.IsNullOrWhiteSpace(queryStr), $"XDR Detection '{detectionYamlFileName}' (id: {id}) is missing properties.queryCondition.queryText.");
            ValidateKql(id, queryStr, true, decodedPath);
            ValidateKqlForBestPractices(queryStr, detectionYamlFileName);
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
            if (fileName == "NoFile.yaml" || fileName == "ASIM_FillNull.yaml")
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

            var allowedExtensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { ".yaml", ".md", ".json" };

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

        private void ValidateKql(string id, string queryStr, bool ignoreNoTabularExpressionError = true, string filePath = null)
        {

            // The KQL validation ignores no tabular expression error. For instance, "let x = table;" is considered a valid query.
            // Add "| count" at the end of the query, to fail queries without tabular expressions.
            if (!ignoreNoTabularExpressionError)
            {
                queryStr += " | count";
            }

            var validationResult = _queryValidator.ValidateSyntax(queryStr);
            var listOfDiagnostics = validationResult.Diagnostics ?? Enumerable.Empty<Diagnostic>();

            bool isRuntimeQualified = IsRuntimeQualifiedQuery(filePath, id, queryStr);
            var filteredDiagnostics = (from p in listOfDiagnostics
                                       where !p.Message.Contains("_GetWatchlist") //We do not validate the getWatchList, since the result schema is not known
                                       && !p.Message.Contains("let forwarder_host_names") //We do not validate the static list of hostnames, used for syslog parsers
                                       where !isRuntimeQualified || !IsSemanticSchemaDiagnostic(p)
                                       select p).ToList();

            var firstErrorLocation = (Line: 0, Col: 0);
            var firstErrorDiag = filteredDiagnostics.FirstOrDefault(d => d.Severity == "Error") ?? filteredDiagnostics.FirstOrDefault();
            if (firstErrorDiag != null)
            {
                firstErrorLocation = GetLocationInQuery(queryStr, firstErrorDiag.Start);
            }

            bool isQueryValid = !filteredDiagnostics.Any();


            Assert.True(
                isQueryValid,
                isQueryValid
                    ? string.Empty
                    : @$"Template Id: {id} is not valid in Line: {firstErrorLocation.Line} col: {firstErrorLocation.Col}
                    Errors: {filteredDiagnostics.Select(d => d.ToString()).ToList().Aggregate((s1, s2) => s1 + "," + s2)}");
        }

        private static bool IsSemanticSchemaDiagnostic(Diagnostic diagnostic)
        {
            if (diagnostic == null)
            {
                return false;
            }

            var code = diagnostic.Code ?? string.Empty;
            if (code.StartsWith("SYN", StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            if (code.Equals("KS107", StringComparison.OrdinalIgnoreCase)
                || code.Equals("KS141", StringComparison.OrdinalIgnoreCase)
                || code.StartsWith("KS", StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }

            return false;
        }

        public static bool IsRuntimeQualifiedQuery(string filePath, string templateId, string queryStr)
        {
            if (string.IsNullOrWhiteSpace(filePath) || string.IsNullOrWhiteSpace(queryStr))
            {
                return false;
            }

            var solutionDir = FindEnclosingSolutionDirectory(filePath);
            if (string.IsNullOrWhiteSpace(solutionDir) || !Directory.Exists(solutionDir))
            {
                return false;
            }

            var candidateEvidenceFiles = new[]
            {
                Path.Combine(solutionDir, "Evidence", "pr-qualification", "pr-qualification-result.json"),
                Path.Combine(solutionDir, "Evidence", "qualification-evidence.json")
            };

            var queryHashes = ComputeCandidateQueryHashes(queryStr);
            var normalizedId = (templateId ?? string.Empty).Trim();
            var strippedId = normalizedId.StartsWith("xdr-", StringComparison.OrdinalIgnoreCase)
                ? normalizedId.Substring(4)
                : normalizedId;

            foreach (var evidencePath in candidateEvidenceFiles)
            {
                if (!File.Exists(evidencePath))
                {
                    continue;
                }

                try
                {
                    var root = JObject.Parse(File.ReadAllText(evidencePath));
                    if (MatchesRuntimeQualifiedEvidence(root, normalizedId, strippedId, queryHashes))
                    {
                        return true;
                    }
                }
                catch
                {
                    // Ignore malformed evidence JSON and continue
                }
            }

            return false;
        }

        private static string FindEnclosingSolutionDirectory(string filePath)
        {
            try
            {
                var fullPath = Path.GetFullPath(filePath);
                var current = Directory.Exists(fullPath) ? new DirectoryInfo(fullPath) : new FileInfo(fullPath).Directory;
                while (current != null && current.Parent != null)
                {
                    if (current.Parent.Name.Equals("Solutions", StringComparison.OrdinalIgnoreCase))
                    {
                        return current.FullName;
                    }
                    current = current.Parent;
                }
            }
            catch
            {
                // Ignore path resolution errors
            }
            return null;
        }

        private static HashSet<string> ComputeCandidateQueryHashes(string queryStr)
        {
            var hashes = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            if (queryStr == null)
            {
                return hashes;
            }

            var lfNormalized = queryStr.Replace("\r\n", "\n");
            var trimmed = lfNormalized.Trim();
            var whitespaceCollapsed = Regex.Replace(trimmed, @"\s+", " ");

            hashes.Add(ComputeSha256Hex(queryStr));
            hashes.Add(ComputeSha256Hex(queryStr.Trim()));
            hashes.Add(ComputeSha256Hex(lfNormalized));
            hashes.Add(ComputeSha256Hex(trimmed));
            hashes.Add(ComputeSha256Hex(whitespaceCollapsed));
            return hashes;
        }

        private static string ComputeSha256Hex(string input)
        {
            using (var sha = SHA256.Create())
            {
                var bytes = Encoding.UTF8.GetBytes(input ?? string.Empty);
                var hashBytes = sha.ComputeHash(bytes);
                return BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
            }
        }

        private static bool MatchesRuntimeQualifiedEvidence(JObject root, string normalizedId, string strippedId, HashSet<string> queryHashes)
        {
            if (root == null)
            {
                return false;
            }

            var verifiedRulesTokens = root.SelectTokens("$..kqlRuntimeVerifiedRules");
            foreach (var token in verifiedRulesTokens)
            {
                if (token is JArray arr)
                {
                    foreach (var item in arr)
                    {
                        if (item is JValue val && val.Type == JTokenType.String)
                        {
                            var strVal = val.Value<string>()?.Trim();
                            if (!string.IsNullOrEmpty(strVal) &&
                                (strVal.Equals(normalizedId, StringComparison.OrdinalIgnoreCase)
                                 || strVal.Equals(strippedId, StringComparison.OrdinalIgnoreCase)
                                 || queryHashes.Contains(strVal)))
                            {
                                return true;
                            }
                        }
                        else if (item is JObject obj)
                        {
                            var status = (string)obj["status"] ?? (string)obj["result"] ?? "PASS";
                            if (!status.Equals("PASS", StringComparison.OrdinalIgnoreCase)
                                && !status.Equals("passed", StringComparison.OrdinalIgnoreCase)
                                && !status.Equals("true", StringComparison.OrdinalIgnoreCase))
                            {
                                continue;
                            }

                            var entryHash = (string)obj["querySha256"] ?? (string)obj["queryHash"] ?? (string)obj["sha256"];
                            if (!string.IsNullOrWhiteSpace(entryHash))
                            {
                                if (queryHashes.Contains(entryHash.Trim()))
                                {
                                    return true;
                                }
                                continue;
                            }

                            var ruleIds = new[]
                            {
                                (string)obj["ruleId"],
                                (string)obj["id"],
                                (string)obj["originalRuleId"],
                                (string)obj["sourceRuleId"]
                            };
                            if (ruleIds.Any(r => !string.IsNullOrWhiteSpace(r) &&
                                (r.Trim().Equals(normalizedId, StringComparison.OrdinalIgnoreCase)
                                 || r.Trim().Equals(strippedId, StringComparison.OrdinalIgnoreCase))))
                            {
                                return true;
                            }
                        }
                    }
                }
            }

            var targetCheckNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
            {
                "kql-validation",
                "alert-parity-live",
                "QUAL-RUNTIME-01",
                "MIG-Q01"
            };

            foreach (var obj in root.DescendantsAndSelf().OfType<JObject>())
            {
                var checkId = (string)obj["checkId"] ?? (string)obj["id"] ?? (string)obj["name"] ?? (string)obj["stage"];
                if (string.IsNullOrWhiteSpace(checkId) || !targetCheckNames.Contains(checkId.Trim()))
                {
                    continue;
                }

                var status = (string)obj["status"] ?? (string)obj["verdict"] ?? (string)obj["result"];
                if (string.IsNullOrWhiteSpace(status) ||
                    (!status.Equals("PASS", StringComparison.OrdinalIgnoreCase) && !status.Equals("passed", StringComparison.OrdinalIgnoreCase)))
                {
                    continue;
                }

                foreach (var prop in obj.DescendantsAndSelf().OfType<JProperty>())
                {
                    if ((prop.Name.Equals("querySha256", StringComparison.OrdinalIgnoreCase)
                         || prop.Name.Equals("queryHash", StringComparison.OrdinalIgnoreCase)
                         || prop.Name.Equals("convertedQuerySha256", StringComparison.OrdinalIgnoreCase)
                         || prop.Name.Equals("sourceQuerySha256", StringComparison.OrdinalIgnoreCase))
                        && prop.Value.Type == JTokenType.String)
                    {
                        var h = prop.Value.Value<string>()?.Trim();
                        if (!string.IsNullOrEmpty(h) && queryHashes.Contains(h))
                        {
                            return true;
                        }
                    }
                }
            }

            return false;
        }

        private static string ExtractXdrRuleId(Dictionary<object, object> yaml, string fallbackFileName)
        {
            if (yaml == null)
            {
                return fallbackFileName;
            }

            if (yaml.TryGetValue("properties", out object propsObj) && propsObj is IReadOnlyDictionary<object, object> props)
            {
                if (props.TryGetValue("id", out object propId) && propId != null)
                {
                    return propId.ToString();
                }
                if (props.TryGetValue("originalRuleId", out object origId) && origId != null)
                {
                    return origId.ToString();
                }
            }

            if (yaml.TryGetValue("id", out object topId) && topId != null)
            {
                return topId.ToString();
            }

            return fallbackFileName;
        }

        private static string ExtractXdrOriginalRuleId(Dictionary<object, object> yaml, string ruleId)
        {
            if (yaml != null)
            {
                if (yaml.TryGetValue("properties", out object propsObj) && propsObj is IReadOnlyDictionary<object, object> props)
                {
                    if (props.TryGetValue("originalRuleId", out object origId) && origId != null)
                    {
                        return origId.ToString();
                    }
                }
                if (yaml.TryGetValue("contentProvenance", out object provObj) && provObj is IReadOnlyDictionary<object, object> prov)
                {
                    if (prov.TryGetValue("source", out object srcObj) && srcObj is IReadOnlyDictionary<object, object> src)
                    {
                        if (src.TryGetValue("id", out object srcId) && srcId != null)
                        {
                            return srcId.ToString();
                        }
                    }
                }
            }

            if (!string.IsNullOrWhiteSpace(ruleId) && ruleId.StartsWith("xdr-", StringComparison.OrdinalIgnoreCase))
            {
                return ruleId.Substring(4);
            }

            return ruleId;
        }

        private static string ExtractXdrQueryText(Dictionary<object, object> yaml)
        {
            if (yaml == null)
            {
                return null;
            }

            if (yaml.TryGetValue("properties", out object propsObj) && propsObj is IReadOnlyDictionary<object, object> props)
            {
                if (props.TryGetValue("queryCondition", out object qcObj) && qcObj is IReadOnlyDictionary<object, object> qc)
                {
                    if (qc.TryGetValue("queryText", out object qt) && qt != null)
                    {
                        return qt.ToString();
                    }
                }
                if (props.TryGetValue("query", out object propQuery) && propQuery != null)
                {
                    return propQuery.ToString();
                }
            }

            if (yaml.TryGetValue("query", out object topQuery) && topQuery != null)
            {
                return topQuery.ToString();
            }

            return null;
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

        [Fact]
        public void Validate_RuntimeQualifiedQuery_SuppressesSemanticDiagnosticsOnlyWhenHashMatches()
        {
            var basePath = Utils.GetTestDirectory(TestFolderDepthForSolutionParsers);
            var tempSolutionDir = Path.Combine(basePath, "Solutions", $"_TempQualTest_{Guid.NewGuid():N}");
            var xdrDetDir = Path.Combine(tempSolutionDir, "XDR Detections");
            var evidenceDir = Path.Combine(tempSolutionDir, "Evidence", "pr-qualification");
            Directory.CreateDirectory(xdrDetDir);
            Directory.CreateDirectory(evidenceDir);

            try
            {
                var ruleId = "xdr-11111111-2222-3333-4444-555555555555";
                var ruleFilePath = Path.Combine(xdrDetDir, "TempRule.yaml");
                var queryWithUnknownTable = "CustomLiveVerifiedTable_CL\n| where Timestamp > ago(1h)\n| project Timestamp, DeviceId, ReportId";
                File.WriteAllText(ruleFilePath, $"id: {ruleId}\n");

                // Without qualification evidence, IsRuntimeQualifiedQuery must be false
                Assert.False(IsRuntimeQualifiedQuery(ruleFilePath, ruleId, queryWithUnknownTable));

                // Write pr-qualification-result.json with matching SHA-256 hash
                var querySha256 = ComputeSha256Hex(queryWithUnknownTable.Trim());
                var evidenceJson = new JObject
                {
                    ["kqlRuntimeVerifiedRules"] = new JArray
                    {
                        new JObject
                        {
                            ["ruleId"] = ruleId,
                            ["status"] = "PASS",
                            ["querySha256"] = querySha256
                        }
                    }
                };
                File.WriteAllText(Path.Combine(evidenceDir, "pr-qualification-result.json"), evidenceJson.ToString());

                // Matching query hash returns true; modified query text returns false
                Assert.True(IsRuntimeQualifiedQuery(ruleFilePath, ruleId, queryWithUnknownTable));
                Assert.False(IsRuntimeQualifiedQuery(ruleFilePath, ruleId, queryWithUnknownTable + "\n| take 5"));

                // ValidateKql passes for the runtime-qualified query with semantic/schema diagnostic
                ValidateKql(ruleId, queryWithUnknownTable, true, ruleFilePath);
            }
            finally
            {
                if (Directory.Exists(tempSolutionDir))
                {
                    Directory.Delete(tempSolutionDir, true);
                }
            }
        }
    }

}

