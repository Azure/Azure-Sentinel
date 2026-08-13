namespace Veeam.Sentinel.FunctionApp.Tests.Client
{
    [TestFixture]
    [Category("UnitTests")]
    public class TlsValidationShould : AuthHandlerTestBase
    {
        [Test]
        public void UsePlatformCertificateValidationForVbr()
        {
            Assert.That(AuthenticatedClientHandler.HasCustomServerCertificateValidationCallback, Is.False);
        }

        [Test]
        public void UsePlatformCertificateValidationForVone()
        {
            using var handler = TestableAuthenticatedVoneClientHandler.InvokeCreateHttpClientHandler();

            Assert.That(handler.ServerCertificateCustomValidationCallback, Is.Null);
        }
    }
}
