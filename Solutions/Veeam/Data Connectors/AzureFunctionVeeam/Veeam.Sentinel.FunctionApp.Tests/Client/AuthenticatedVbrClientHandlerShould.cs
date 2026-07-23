using NSubstitute;
using NUnit.Framework.Internal;
using Sentinel.Client;
using Sentinel.DTOs;
using Veeam.Sentinel.FunctionApp.Tests.Logger;
using Sentinel.Managers;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1;
using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Client;

using Veeam.AC.VBR.ApiClient.Api.v1_2_rev1.Models;


namespace Veeam.Sentinel.FunctionApp.Tests.Client
{
    public abstract class AuthHandlerTestBase
    {
        protected TestLogger<AuthenticatedVbrClientHandler> Logger { get; private set; }
        protected ISecretsManager SecretsManager { get; private set; }
        protected ILoginApi LoginApi { get; private set; }
        protected TestableAuthenticatedVbrClientHandler AuthenticatedClientHandler { get; private set; }
        protected CancellationToken DefaultCancellationToken => CancellationToken.None;

        [SetUp]
        public void SetUp()
        {
            Logger = new TestLogger<AuthenticatedVbrClientHandler>(); // stub
            SecretsManager = Substitute.For<ISecretsManager>(); // stub
            LoginApi = Substitute.For<ILoginApi>(); // mock

            AuthenticatedClientHandler = new TestableAuthenticatedVbrClientHandler(
                LoginApi,
                TestConstants.BaseUrl,
                TestConstants.VbrId,
                SecretsManager,
                Logger);
        }

        [TearDown]
        public void Cleanup()
        {
            AuthenticatedClientHandler?.Dispose();
        }

        #region Arrange helpers

        protected void SetupValidCredentials() =>
            SecretsManager.GetVbrCredentialsAsync(TestConstants.VbrId)
                   .Returns(new Credentials(TestConstants.ValidUsername, TestConstants.ValidPassword));

        protected void SetupInvalidCredentials() =>
            SecretsManager.GetVbrCredentialsAsync(TestConstants.VbrId)
                   .Returns(new Credentials(TestConstants.ValidUsername, TestConstants.InValidPassword));

        protected void ArrangeCurrentKeyVaultTokens(string accessToken, string refreshToken) =>
            SecretsManager.GetTokensAsync(TestConstants.VbrId)
                   .Returns(new Tokens(accessToken, refreshToken));

        protected static TokenModel GoodTokens() => new()
        {
            AccessToken = TestConstants.GoodAccessToken,
            RefreshToken = TestConstants.GoodRefreshToken
        };

        protected void ArrangeLoginApi(TokenModel tokens)
        {
            _vbrCreateTokenCallCount = 0;

            LoginApi.CreateTokenAsync(Arg.Any<TokenLoginSpec>()).Returns(
                call =>
                {
                    _vbrCreateTokenCallCount++;

                    var spec = call.Arg<TokenLoginSpec>();

                    if (spec.GrantType == ELoginGrantType.Password && IsValidPassword(spec)
                    || spec.GrantType == ELoginGrantType.Refresh_token && spec.RefreshToken == TestConstants.GoodRefreshToken)
                        return tokens;

                    throw new ApiException(401, "Invalid credentials");
                }
                );
        }

        private static bool IsValidPassword(TokenLoginSpec spec) =>
            spec.Username == TestConstants.ValidUsername &&
            spec.Password == TestConstants.ValidPassword;


        #endregion

        #region Request helpers

        protected Func<CancellationToken, Task<string>> SimulateRequest(bool isUnauthorized = false)
        {
            // if isUnauthorized is equal to true => we simulate that vbr returned 401, during its call 
            _requestCallCount = 0;
            return _ =>
            {
                _requestCallCount++;

                if (isUnauthorized && _requestCallCount == 1)
                    throw new ApiException(401, "Access token expired");

                return Task.FromResult("OK");
            };
        }

        private int _vbrCreateTokenCallCount;
        private int _requestCallCount;
        protected int VbrCreateTokenCallCount => _vbrCreateTokenCallCount;
        protected int RequestInvocationCount => _requestCallCount;

        #endregion
    }

    [TestFixture]
    [Category("UnitTests")]
    public class TestableAuthenticatedVbrClientHandlerShould : AuthHandlerTestBase
    {
        [Test]
        public async Task CallCreateTokensOnce_WhenValidCredentialsProvided()
        {
            SetupValidCredentials();

            var vbrReturnsTokens = GoodTokens();
            ArrangeLoginApi(vbrReturnsTokens);
            var request = SimulateRequest();
            var result = await AuthenticatedClientHandler.InvokeSendAsync(request, default);

            Assert.That(result, Is.EqualTo("OK"));
            Assert.That(RequestInvocationCount, Is.EqualTo(1));
            Assert.That(VbrCreateTokenCallCount, Is.EqualTo(1));
        }

        [Test]
        public void CallCreateTokensOnce_ThrowException_WhenInvalidCredentials()
        {
            SetupInvalidCredentials();

            var vbrReturnsTokens = GoodTokens();
            ArrangeLoginApi(vbrReturnsTokens);

            var request = SimulateRequest();

            Assert.ThrowsAsync<ApiException>(async () =>
            {
                await AuthenticatedClientHandler.InvokeSendAsync(request, DefaultCancellationToken);
            });

            Assert.That(RequestInvocationCount, Is.EqualTo(0));
            Assert.That(VbrCreateTokenCallCount, Is.EqualTo(1));
        }

        [Test]
        public async Task CallRequestTwiceAndCreateTokenTwice_WhenExpiredAccessTokenGoodRefreshToken()
        {
            SetupValidCredentials();
            ArrangeCurrentKeyVaultTokens(TestConstants.ExpiredAccessToken, TestConstants.GoodRefreshToken);

            ArrangeLoginApi(GoodTokens());

            var warmUp = SimulateRequest(); // simulate that some tokens are present
            var warmUpResult = await AuthenticatedClientHandler.InvokeSendAsync(warmUp, DefaultCancellationToken);

            Assert.That(warmUpResult, Is.EqualTo("OK"));
            Assert.That(RequestInvocationCount, Is.EqualTo(1));
            Assert.That(VbrCreateTokenCallCount, Is.EqualTo(1)); // init

            var retrying = SimulateRequest(isUnauthorized: true);
            var result = await AuthenticatedClientHandler.InvokeSendAsync(retrying, DefaultCancellationToken);

            Assert.That(result, Is.EqualTo("OK"));
            Assert.That(RequestInvocationCount, Is.EqualTo(2));
            Assert.That(VbrCreateTokenCallCount, Is.EqualTo(2)); // init, update using token
        }

        [Test]
        public async Task CallRequestTwiceAndCreateTokenTwice_WhenExpiredAccessTokenExpiredRefreshToken()
        {
            SetupValidCredentials();
            ArrangeCurrentKeyVaultTokens(TestConstants.ExpiredAccessToken, TestConstants.ExpiredRefreshToken);

            ArrangeLoginApi(GoodTokens());

            var simulateExpiredTokens = SimulateRequest();
            var warmUpResult = await AuthenticatedClientHandler.InvokeSendAsync(simulateExpiredTokens, DefaultCancellationToken);

            Assert.That(warmUpResult, Is.EqualTo("OK"));
            Assert.That(RequestInvocationCount, Is.EqualTo(1));
            Assert.That(VbrCreateTokenCallCount, Is.EqualTo(1)); // init

            var retrying = SimulateRequest(isUnauthorized: true);
            var result = await AuthenticatedClientHandler.InvokeSendAsync(retrying, DefaultCancellationToken);

            Assert.That(result, Is.EqualTo("OK"));
            Assert.That(RequestInvocationCount, Is.EqualTo(2));
            Assert.That(VbrCreateTokenCallCount, Is.EqualTo(3)); // init, update using token, update using password
        }
    }
}
