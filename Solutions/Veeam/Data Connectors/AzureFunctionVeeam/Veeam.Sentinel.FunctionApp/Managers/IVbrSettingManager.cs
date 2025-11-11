namespace Sentinel.Managers
{
    internal interface IVbrSettingManager
    {
        Task<string> GetVbrBaseUrlAsync(string vbrId);

        Task<string> GetVbrPasswordAliasAsync(string vbrId);

        Task<string> GetVbrUsernameAliasAsync(string vbrId);
    }
}