using Moq;
using Microsoft.Extensions.Logging;
using Varonis.Sentinel.Functions.Helpers;

namespace Varonis.Sentinel.Test
{
    [TestClass]
    public sealed class CustomParserTest
    {
        [TestMethod]
        [DataRow("rule without quotes, \"with quotes and space before cell\",\"with comma, in the cell\"")]
        [DataRow("\"with quotes\", rule without quotes and with space befor cell,\"with comma, in the cell\"")]
        [DataRow("\"with quotes\",,\"with comma, in the cell\",rule without quotes,")]

        public void CsvParsingTestSuccess(string csv)
        {
            var logger = new Mock<ILogger>();

            var parser = new CustomParser(logger.Object);
            var result = parser.ParseCsvToArray(csv);

            Assert.AreEqual(3, result.Length);
            logger.Verify(
                x => x.Log(
                    LogLevel.Error,
                    It.IsAny<EventId>(),
                    It.IsAny<It.IsAnyType>(),
                    It.IsAny<Exception>(),
                    (Func<It.IsAnyType, Exception, string>)It.IsAny<object>()),
                Times.Never
             );
        }

        [TestMethod]
        [DataRow("rule without quotes, \"with quotes and space before cell\",\"with comma, \"in the cell\"")]
        [DataRow("\"with quotes\",\",\"with comma, in the cell\",rule without quotes,")]

        public void CsvParsingTestFailed(string csv)
        {
            var logger = new Mock<ILogger>();

            var parser = new CustomParser(logger.Object);
            var result = parser.ParseCsvToArray(csv);

            Assert.AreEqual(0, result.Length);
            logger.Verify(
                x => x.Log(
                    LogLevel.Error,
                    It.IsAny<EventId>(),
                    It.IsAny<It.IsAnyType>(),
                    It.IsAny<Exception>(),
                    (Func<It.IsAnyType, Exception, string>)It.IsAny<object>()),
                Times.Once
             );
        }

        [TestMethod]

        public void ParstTokenInfoTestSuccess()
        {
            var json = "{\"access_token\":\"token_value\",\"token_type\":\"Bearer\",\"expires_in\":3600}";
            var logger = new Mock<ILogger>();
            var parser = new CustomParser(logger.Object);

            var result = parser.ParseTokenInfo(json);

            Assert.IsNotNull(result);
            Assert.AreEqual("token_value", result.Value.token);
            Assert.AreEqual("Bearer", result.Value.token_type);
            Assert.AreEqual(3600, result.Value.expiresIn);
        }
    }
}
