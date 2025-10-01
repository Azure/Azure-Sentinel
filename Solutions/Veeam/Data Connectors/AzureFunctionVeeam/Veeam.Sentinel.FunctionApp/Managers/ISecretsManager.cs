using Sentinel.DTOs;

namespace Sentinel.Managers
{
    public interface ISecretsManager
    {
        Task SaveTokensAsync(string vbrId, Tokens tokens);

        Task<Tokens> GetTokensAsync(string vbrId);

        Task<Credentials> GetVbrCredentialsAsync(string vbrId);

        Task<string> GetVbrBaseUrlAsync(string vbrId);

        Task<Credentials> GetVoneCredentialsAsync(string voneId);
        
        Task<string> GetVoneBaseUrlAsync(string voneId);
        
        Task<CovewareCredentials> GetCowareCredentialsAsync(string cowareId);
        
        Task SaveCovewareTokensAsync(string covewareId, CovewareTokens tokens);
        
        Task<CovewareTokens> GetCovewareTokensAsync(string covewareId);
    }
}