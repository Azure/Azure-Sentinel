namespace Sentinel.Managers
{
    internal interface ICovewareSettingManager
    {
        Task<string> GetCovewarePasswordAliasAsync(string cowareId);
        Task<string> GetCovewareUsernameAliasAsync(string cowareId);
        Task<string> GetCovewareClientIdAliasAsync(string cowareId);
    }
}
