using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text.RegularExpressions;
using Kusto.Language;
using Kusto.Language.Symbols;
using Xunit;
using YamlDotNet.Serialization;

namespace Kqlvalidations.Tests
{
    // Local regex/structure regression tests, not live DCR compilation or enablement.
    public class ProofpointIngestionIpValidationTests
    {
        private static readonly string Query = LoadQuery();
        private static readonly string TailPattern = Regex.Match(Query, "replace_regex\\(RelayIp, @\"([^\"]*)\"")
            .Groups[1].Value;
        private static readonly string[] Patterns = Regex.Matches(Query, "matches regex @\"([^\"]*)\"")
            .Cast<Match>().Select(match => match.Groups[1].Value).ToArray();

        private static string LoadQuery()
        {
            var path = Path.Combine(Utils.GetTestDirectory(6), "Parsers", "ASimEmailEvent",
                "IngestTimeParsers", "ASimEmailEventProofpointPODMailLog.yaml");
            var parser = new DeserializerBuilder().Build()
                .Deserialize<Dictionary<string, object>>(File.ReadAllText(path));
            return (string)parser["ParserQuery"];
        }

        private static bool IsValid(string ip)
        {
            var normalized = Regex.Replace(ip, TailPattern, ":0:0");
            var maxComponents = normalized.StartsWith(":", StringComparison.Ordinal)
                || normalized.EndsWith(":", StringComparison.Ordinal) ? 9 : 8;
            return Regex.IsMatch(ip, Patterns[0])
                || Regex.IsMatch(normalized, Patterns[1])
                || (Regex.IsMatch(normalized, Patterns[2]) && normalized.Split(':').Length <= maxComponents);
        }

        [Fact]
        public void QueryRemainsSourceRootedAndUsesInlineValidation()
        {
            Assert.StartsWith("source\n", Query.Replace("\r\n", "\n"));
            Assert.DoesNotContain("let ", Query);
            Assert.DoesNotContain("IsValidIpAddress", Query);
            Assert.DoesNotContain("parse_ipv4", Query);
            Assert.DoesNotContain("parse_ipv6", Query);
            Assert.Contains("| parse Relay with RelayHost \" [\" RelayIp \"]\" *", Query);
            Assert.Equal(3, Patterns.Length);
            Assert.NotEmpty(TailPattern);
            Assert.Contains("replace_regex(RelayIp, @\"" + TailPattern + "\", \":0:0\")", Query);
            Assert.Contains("RelayIp matches regex @\"" + Patterns[0] + "\"", Query);
            Assert.Contains("_RelayIpForValidation matches regex @\"" + Patterns[1] + "\"", Query);
            Assert.Contains("_RelayIpForValidation matches regex @\"" + Patterns[2] + "\"", Query);
            Assert.Contains("and array_length(split(_RelayIpForValidation, \":\")) <= iff(_RelayIpForValidation startswith \":\" or _RelayIpForValidation endswith \":\", 9, 8))", Query);
            Assert.Contains("RelayIp, \"\"),", Query);
            Assert.Contains("SrcIpAddr = iff(IsDelivery, \"\", RelayIp)", Query);
            Assert.Contains("DstIpAddr = iff(IsDelivery, RelayIp, \"\")", Query);
            Assert.DoesNotContain("_RelayIpForValidation", Query.Substring(Query.LastIndexOf("| project\n", StringComparison.Ordinal)));
            Assert.Empty(KustoCode.Parse(Query).GetDiagnostics());
            var source = new TableSymbol("source",
                "(TimeGenerated:datetime, eventTime:datetime, sm:dynamic, pps:dynamic, metadata:dynamic, tls:dynamic, id:string, data:string)");
            var globals = GlobalState.Default.WithDatabase(new DatabaseSymbol("Local", source));
            Assert.Empty(KustoCode.ParseAndAnalyze(Query, globals).GetDiagnostics());
        }

        [Theory]
        [InlineData("0.0.0.0", true)]
        [InlineData("255.255.255.255", true)]
        [InlineData("192.0.2.1", true)]
        [InlineData("2001:db8:0:0:0:0:0:1", true)]
        [InlineData("ABCD:EF01:2345:6789:ABCD:EF01:2345:6789", true)]
        [InlineData("::", true)]
        [InlineData("::1", true)]
        [InlineData("2001:db8::", true)]
        [InlineData("2001:db8::1", true)]
        [InlineData("::ffff:192.0.2.1", true)]
        [InlineData("2001:db8::1:192.0.2.1", true)]
        [InlineData("2001:db8:0:0:0:1:192.0.2.1", true)]
        [InlineData("", false)]
        [InlineData("host.example", false)]
        [InlineData("256.1.2.3", false)]
        [InlineData("1.2.3", false)]
        [InlineData("1.2.3.4.5", false)]
        [InlineData("01.2.3.4", false)]
        [InlineData("192.0.2.1/24", false)]
        [InlineData("2001:db8::1/64", false)]
        [InlineData("fe80::1%eth0", false)]
        [InlineData("[::1]", false)]
        [InlineData(" 192.0.2.1", false)]
        [InlineData("192.0.2.1\n", false)]
        [InlineData("::1\n", false)]
        [InlineData("1:2:3:4:5:6:7", false)]
        [InlineData("1:2:3:4:5:6:7:8:9", false)]
        [InlineData("1:2:3:4:5:6:7:8::", false)]
        [InlineData("1::2::3", false)]
        [InlineData(":::1", false)]
        [InlineData("12345::1", false)]
        [InlineData("gggg::1", false)]
        [InlineData("::ffff:256.0.2.1", false)]
        [InlineData("::ffff:0192.0.2.1", false)]
        [InlineData("1:2:3:4:5:6:7:192.0.2.1", false)]
        [InlineData("abcd::1234:1234:1234:1234:1234:192.0.2.1", false)]
        public void ValidatesAddressLiterals(string ip, bool expected)
        {
            Assert.Equal(expected, IsValid(ip));
        }

        [Fact]
        public void AllCompressionPositionsAndGroupCountsAreValidated()
        {
            for (var left = 0; left <= 9; left++)
            {
                for (var right = 0; right <= 9; right++)
                {
                    var prefix = string.Join(":", Enumerable.Repeat("abcd", left));
                    var suffix = string.Join(":", Enumerable.Repeat("1234", right));
                    CheckAddress(prefix + "::" + suffix, left + right < 8);
                    CheckAddress(prefix + "::" + (right == 0 ? "" : suffix + ":") + "192.0.2.1",
                        left + right + 2 < 8);
                }
                CheckAddress(string.Join(":", Enumerable.Repeat("abcd", left)), left == 8);
                CheckAddress(string.Concat(Enumerable.Repeat("abcd:", left)) + "192.0.2.1", left == 0 || left == 6);
            }
        }

        [Fact]
        public void Ipv4OctetBoundariesAreValidated()
        {
            foreach (var octet in new[] { "-1", "0", "1", "9", "10", "99", "100", "199", "200", "249", "250", "255", "256", "999", "01", "000" })
            {
                for (var position = 0; position < 4; position++)
                {
                    var octets = new[] { "192", "0", "2", "1" };
                    octets[position] = octet;
                    var ip = string.Join(".", octets);
                    var expected = int.TryParse(octet, out var value) && value >= 0 && value <= 255
                        && (octet.Length == 1 || octet[0] != '0');
                    CheckAddress(ip, expected);
                    CheckAddress("2001:db8::1:" + ip, expected);
                }
            }
        }

        private static void CheckAddress(string ip, bool expected)
        {
            Assert.True(IsValid(ip) == expected, "Validation mismatch: " + ip);
            if (expected)
            {
                Assert.True(IPAddress.TryParse(ip, out _), "Valid literal rejected by IPAddress: " + ip);
            }
        }
    }
}
