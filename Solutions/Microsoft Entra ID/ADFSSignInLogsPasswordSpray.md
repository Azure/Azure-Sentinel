### Connect Health and Azure Sign-ins Data for ADFS

| Error code | Error number | Description | Remediation information |
|-----------|---------------|-------------|--------------------------|
| TokenIssuanceError | 50000 | The user was not able to sign in because of issuance authorization errors. | Check the Issuance Authorization rules and check if it has "Permit All". If not, go through the custom authorization rules to check if the condition in that rule will evaluate true for the affected user. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| InvalidRelyingPartyError | 50001 | The user was not able to sign in because the resource being accessed is disabled or the name could not be found. This can happen if the application has not been installed by the administrator of the tenant, or if the resource principal was not found in the directory or is invalid due to a typo. | Check your app's code to ensure that you have specified the exact and correct resource URL for the resource you are trying to access. Please see the returned exception message for details. |
| CertificateValidationFailed | 50017 | The user was not able to sign in because certificate based authentication failed. | [Troubleshoot certificate based authentication](https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/user-prov-sync/certificate-based-authenticate-issue) For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| UserDisabled | 50057 | The user was not able to sign in because the user's account is disabled. | Verify if account has been locked out in Active Directory and re-enable the user if necessary. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| InvalidUserNameOrPassword | 50126 | The user was not able to sign in because the user did not enter the right credentials. | Check if the affected user's password is incorrect, newly changed, or expired. If these do not apply, check service account permissions and AD trust. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| InvalidPasswordExpiredOnPremPassword | 50144 | The user was not able to sign in because the user's password is expired. | The user should change their password at the next attempted log in. |
| DeviceAuthenticationFailed | 50155 | The user was not able to sign in because device authentication failed. | Verify that the device is synced from cloud to on-prem or is not disabled. Sync cycles may be delayed since it syncs the Key after the object is synced. |
| UnspecifiedError | 90000 | Catch call for any other error conditions. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. | 
| AuthorityCertificateResolveError | 300010 | The user was not able to sign in because AD FS rejected the token from a 3rd party IDP. | Verify the correct configuration of the signing certificate and encyrption certificate on AD FS and the Claims Provider Trust. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| MfaTokenValidationFailure | 300020 | The use was not able to sign in because to a problem during token validation at the MFA layer. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| AccountExtranetLockedOut | 300030 | The user was not able to sign in because the user was locked out from the extranet. | Reset the user lockout with Reset-ADFSAccountLockout Powershell commandlet. For additional information on ESL, view this [document](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/operations/configure-ad-fs-extranet-smart-lockout-protection).
| WsFedRequestFailure | 300040 | The user was not able to sign in because AD FS rejected the WS Federation passive request because it is malformed or invalid. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in.
| OAuthRequestFailure | 400000 | Catch call for uncategorized Oauth request failures. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthAuthCodeIssuanceFailure | 400010 | The Federation Service failed to issue OAuth authorization code. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthAccessTokenIssuanceFailure | 400020 | The Federation Service failed to issue an OAuth access token | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthIdTokenIssuanceFailure | 400030 | The Federation Service failed to issue an ID token. | To create an ID token, the user identifier should be available in the "AnchorClaimType" claim configured in the Claims Provider trust. If the user is authenticated by a different Claims Provider, make sure the "AnchorClaimType" is set to a claim that the Claims Provider issues in the token to AD FS. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthNextGenCredsIssuanceFailure | 400040 | The Federation Service failed to issue an OAuth Primary Refresh Token. | The Primary Refresh token performs device authentication. For Azure AD devices, please make sure device sync is enabled. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthWinHelloCertIssuanceFailure | 400050 | The Federation Service failed to issue an OAuth WinHello for Business Certificate. | Please verify if the WHB certificate configuration is set properly using the "Get-AdfsCertificateAuthority" commandlet. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthClientAuthenticationFailure | 400060 | The Federation Service failed to authenticate the OAuth Client. | Please verify if the client credential used by the OAuth client is configured in AD FS (under OAuth Client configurations) and is valid. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. | 
| OAuthOnBehalfOfTokenIssuanceFailure | 400070 | The Federation Service failed to issue an OAuth access token as a result of an error while processing the OAuth On Behalf Of token request. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthLogonCertIssuanceFailure | 400080 | The Federation Service failed to issue Logon Certificate as a result of an error while processing the OAuth Logon Certificate token request. | Please verify if the Logon certificate configuration is set properly using the "Get-AdfsCertificateAuthority" commandlet. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |
| OAuthVpnCertIssuanceFailure | 400090 | The Federation Service failed to issue VPN Certificate as a result of an error while processing the OAuth VPN Certificate token request. | Please verify if the VPN certificate configuration is set properly using the "Get-AdfsCertificateAuthority" commandlet. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. | 
| OAuthClientCredsFailure | 400100 | The Federation Service failed to issue an OAuth access token as a result of an error while processing the OAuth Client Credentials request. | For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. | 
| InvalidClientApplicationError | 901125 | The user was not able to sign in because AD FS rejected the request made to access invalid/disabled client application. | Check if the application/client id that is specified is valid and/or registered with AD FS and is enabled. For additional details, check the AD FS logs with the correlation ID and Server Name from the sign-in. |

















