using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Kusto.Language;
using Kusto.Language.Symbols;
using Kusto.Language.Syntax;
using Microsoft.VisualBasic.FileIO;
using Newtonsoft.Json.Linq;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    public class ASimEmailEventsTests
    {
        private static readonly string Root = Utils.GetTestDirectory(6);
        private const string Suffix = "EmailEventMicrosoftDefenderOffice365";

        private static Dictionary<string, object> Parser(string prefix)
        {
            var path = Path.Combine(Root, "Parsers", "ASimEmailEvent", "Parsers", prefix + Suffix + ".yaml");
            return new DeserializerBuilder().Build().Deserialize<Dictionary<string, object>>(File.ReadAllText(path));
        }

        private static string Declaration(Dictionary<string, object> parser)
        {
            var parameters = (IEnumerable<object>)parser["ParserParams"];
            var signature = string.Join(", ", parameters.Cast<Dictionary<object, object>>().Select(p =>
            {
                var value = p["Default"];
                var literal = p["Type"].ToString() == "string" ? "'" + value + "'"
                    : value is bool flag ? flag.ToString().ToLowerInvariant() : value.ToString();
                return p["Name"] + ":" + p["Type"] + "=" + literal;
            }));
            return "let " + parser["ParserName"] + " = (" + signature + ") {\n" + parser["ParserQuery"] + "\n};\n";
        }

        private static GlobalState Globals(bool optionalColumns = true)
        {
            var path = Path.Combine(Root, ".script", "tests", "KqlvalidationsTests", "CustomTables", "EmailEvents.json");
            var schema = JObject.Parse(File.ReadAllText(path));
            var columns = schema["Properties"]
                .Where(p => optionalColumns || !new[] { "To", "Cc", "EmailSize" }.Contains((string)p["name"]))
                .Select(p => new ColumnSymbol((string)p["name"], ScalarTypes.GetSymbol((string)p["type"])));
            return GlobalState.Default.WithDatabase(new DatabaseSymbol("Synthetic", new TableSymbol("EmailEvents", columns)));
        }

        private static KustoCode Analyze(string query, bool optionalColumns = true)
        {
            var code = KustoCode.ParseAndAnalyze(query, Globals(optionalColumns));
            var errors = code.GetDiagnostics().Where(d => d.Severity == "Error").ToList();
            Assert.True(errors.Count == 0, string.Join(Environment.NewLine, errors.Select(e => e.Message + " at " + e.Start)));
            return code;
        }

        [Theory]
        [InlineData("ASim", true)]
        [InlineData("vim", true)]
        [InlineData("ASim", false)]
        [InlineData("vim", false)]
        public void ParserBindsWithAndWithoutOptionalSourceColumns(string prefix, bool optionalColumns)
        {
            var parser = Parser(prefix);
            var code = Analyze(Declaration(parser) + parser["ParserName"] + "()", optionalColumns);
            Assert.IsType<TableSymbol>(code.ResultType);
        }

        [Theory]
        [InlineData("ASim")]
        [InlineData("vim")]
        public void OutputMatchesAuthoritativeEmailEventFieldNamesAndTypes(string prefix)
        {
            var parser = Parser(prefix);
            var code = Analyze(Declaration(parser) + parser["ParserName"] + "()");
            var output = Assert.IsType<TableSymbol>(code.ResultType).Columns.ToDictionary(c => c.Name, c => c.Type.Name);
            var specification = new Dictionary<string, (string Type, string Class)>();
            using (var csv = new TextFieldParser(Path.Combine(Root, "ASIM", "dev", "ASimTester", "ASimTester.csv")))
            {
                csv.SetDelimiters(",");
                csv.ReadFields();
                var rows = new List<string[]>();
                while (!csv.EndOfData)
                    rows.Add(csv.ReadFields());
                foreach (var row in rows.Where(r => r[3] == "Common").Concat(rows.Where(r => r[3] == "EmailEvent")))
                    specification[row[0]] = (row[1], row[2]);
            }
            foreach (var field in output)
            {
                Assert.True(specification.ContainsKey(field.Key), "Unnormalized output: " + field.Key);
                Assert.Equal(specification[field.Key].Type, field.Value);
            }
            foreach (var field in specification.Where(p => p.Value.Class == "Mandatory"))
                Assert.True(output.ContainsKey(field.Key), "Missing mandatory output: " + field.Key);
        }

        [Fact]
        public void VariantsHaveIdenticalSchemasAndPreserveOneSourceRead()
        {
            var schemas = new List<string[]>();
            foreach (var prefix in new[] { "ASim", "vim" })
            {
                var parser = Parser(prefix);
                var code = Analyze(Declaration(parser) + parser["ParserName"] + "()");
                schemas.Add(Assert.IsType<TableSymbol>(code.ResultType).Columns.Select(c => c.Name + ":" + c.Type.Name).ToArray());
                var sourceReads = code.Syntax.GetDescendants<NameReference>()
                    .Where(n => n.ReferencedSymbol is TableSymbol table && table.Name == "EmailEvents").ToList();
                Assert.Single(sourceReads);
                var prohibited = new[] { "MvExpandOperator", "MvApplyOperator", "SummarizeOperator", "DistinctOperator", "JoinOperator" };
                Assert.DoesNotContain(code.Syntax.GetDescendants<QueryOperator>(), op => prohibited.Contains(op.GetType().Name));
            }
            Assert.Equal(schemas[0], schemas[1]);
        }

        private static string SourceHash(string content)
        {
            var normalized = content.Replace("\r\n", "\n").Replace("\r", "\n");
            return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(normalized))).ToLowerInvariant();
        }

        [Theory]
        [InlineData("\n")]
        [InlineData("\r\n")]
        public void SyntheticRegressionQueryBindsWithoutAnyExternalTables(string lineEnding)
        {
            var path = Path.Combine(Root, "Parsers", "ASimEmailEvent", "Tests", "EmailEventsRegression.kql");
            var query = File.ReadAllText(path);
            foreach (var name in new[] { "ASim" + Suffix, "vim" + Suffix, "vimEmailEventEmpty", "ASimEmailEvent", "imEmailEvent" })
            {
                var source = Path.Combine(Root, "Parsers", "ASimEmailEvent", "Parsers", name + ".yaml");
                var content = File.ReadAllText(source).Replace("\r\n", "\n").Replace("\r", "\n");
                var hash = SourceHash(content.Replace("\n", lineEnding));
                Assert.Contains("// source-sha256 " + name + ": " + hash, query);
            }
            var code = KustoCode.ParseAndAnalyze(query, GlobalState.Default);
            var errors = code.GetDiagnostics().Where(d => d.Severity == "Error").ToList();
            Assert.True(errors.Count == 0, string.Join(Environment.NewLine,
                errors.Select(e => e.Message + " at " + e.Start + ": " + query.Substring(Math.Max(0, e.Start - 50), Math.Min(180, query.Length - Math.Max(0, e.Start - 50))))));
            Assert.IsType<TableSymbol>(code.ResultType);
        }
    }
}
