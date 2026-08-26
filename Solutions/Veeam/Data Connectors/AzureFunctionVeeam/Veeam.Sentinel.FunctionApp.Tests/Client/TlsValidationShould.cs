using Sentinel.Client;
using Veeam.Sentinel.FunctionApp.Tests.Logger;

namespace Veeam.Sentinel.FunctionApp.Tests.Client
{
    [TestFixture]
    [Category("UnitTests")]
    public class TlsValidationShould : AuthHandlerTestBase
    {
        [Test]
        public void UsePlatformCertificateValidationForVbr()
        {
            TestableAuthenticatedVbrClientHandler vbrClientHandler = AuthenticatedClientHandler;

            Assert.That(vbrClientHandler.HasCustomRemoteCertificateValidationCallback, Is.False);
        }

        [Test]
        public void UsePlatformCertificateValidationForVone()
        {
            using var voneClientHandler = new TestableAuthenticatedVoneClientHandler(
                TestConstants.BaseUrl,
                "test-vone",
                SecretsManager,
                new TestLogger<AuthenticatedVoneClientHandler>());

            Assert.That(voneClientHandler.HasCustomServerCertificateValidationCallback, Is.False);
        }
    }
}
