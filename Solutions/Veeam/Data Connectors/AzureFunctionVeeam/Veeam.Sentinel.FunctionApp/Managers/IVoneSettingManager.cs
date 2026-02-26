namespace Sentinel.Managers
{
    internal interface IVoneSettingManager
    {
        Task<string> GetVoneBaseUrlAsync(string voneId);

        Task<string> GetVonePasswordAliasAsync(string voneId);

        Task<string> GetVoneUsernameAliasAsync(string voneId);
    }
}