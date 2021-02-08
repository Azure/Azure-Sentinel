namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model
{
    public enum AttackTactic
    {
        InitialAccess,
        Execution,
        Persistence,
        PrivilegeEscalation,
        DefenseEvasion,
        CredentialAccess,
        Discovery,
        LateralMovement,
        Collection,
        Exfiltration,
        CommandAndControl,
        Impact,
        PreAttack
    }
}
