using System;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public enum Tactic
    {
        /// <summary>
        /// Unknown alert intent is the default value for the <see cref="Tactic"/> enumeration. 
        /// Some alert providers won't tag alerts at first stage with intents, so having a default unknown values helps make this field optional in the 
        /// </summary>
        Unknown = 0,

        /// <summary>
        /// PreAttack is any attempt to gather information or failed attempt to gain access to a target system prior to exploitation. 
        /// This step is usually detected as an attempt originating from outside the network in attempt to scan the target system to find a way in.
        /// </summary>
        PreAttack = 1,

        /// <summary>
        /// InitialAccess is the stage where an attacker manage to get foothold on the attacked resource. 
        /// This stage is applicable not only for compute hosts, but also for resources such as user accounts, certificates etc..
        /// Adversaries will often be able to control the resource after this stage.
        /// </summary>
        InitialAccess = 2,

        /// <summary>
        /// Persistence is any access, action, or configuration change to a system that gives an adversary a persistent presence on that system. 
        /// Adversaries will often need to maintain access to systems through interruptions such as system restarts, loss of credentials, or other 
        /// failures that would require a remote access tool to restart or alternate backdoor for them to regain access
        /// </summary>
        Persistence = 4,

        /// <summary>
        /// Privilege escalation is the result of actions that allow an adversary to obtain a higher level of permissions on a system or network. 
        /// Certain tools or actions require a higher level of privilege to work and are likely necessary at many points throughout an operation.
        /// User accounts with permissions to access specific systems or perform specific functions necessary for adversaries to achieve their objective may also be considered an escalation of privilege. 
        /// </summary>
        PrivilegeEscalation = 8,

        /// <summary>
        /// Defense evasion consists of techniques an adversary may use to evade detection or avoid other defenses. Sometimes these actions are the 
        /// same as or variations of techniques in other categories that have the added benefit of subverting a particular defense or mitigation. 
        /// </summary>
        DefenseEvasion = 16,

        /// <summary>
        /// Credential access represents techniques resulting in access to or control over system, domain, or service credentials that are used within an enterprise environment. 
        /// Adversaries will likely attempt to obtain legitimate credentials from users or administrator accounts (local system administrator or domain users with administrator access) to use within the network. 
        /// With sufficient access within a network, an adversary can create accounts for later use within the environment. 
        /// </summary>
        CredentialAccess = 32,

        /// <summary>
        /// Discovery consists of techniques that allow the adversary to gain knowledge about the system and internal network. 
        /// When adversaries gain access to a new system, they must orient themselves to what they now have control of and what benefits operating from that system give to their current objective or overall goals during the intrusion. 
        /// The operating system provides many native tools that aid in this post-compromise information-gathering phase. 
        /// </summary>
        Discovery = 64,

        /// <summary>
        /// Lateral movement consists of techniques that enable an adversary to access and control remote systems on a network and could, but does not necessarily, include execution of tools on remote systems. 
        /// The lateral movement techniques could allow an adversary to gather information from a system without needing additional tools, such as a remote access tool.
        /// An adversary can use lateral movement for many purposes, including remote Execution of tools, pivoting to additional systems, access to specific information or files, access to additional credentials, or to cause an effect. 
        /// </summary>
        LateralMovement = 128,

        /// <summary>
        /// The execution tactic represents techniques that result in execution of adversary-controlled code on a local or remote system. 
        /// This tactic is often used in conjunction with lateral movement to expand access to remote systems on a network. 
        /// </summary>
        Execution = 256,

        /// <summary>
        /// Collection consists of techniques used to identify and gather information, such as sensitive files, from a target network prior to exfiltration. 
        /// This category also covers locations on a system or network where the adversary may look for information to exfiltrate.
        /// </summary>
        Collection = 512,

        /// <summary>
        /// Exfiltration refers to techniques and attributes that result or aid in the adversary removing files and information from a target network. 
        /// This category also covers locations on a system or network where the adversary may look for information to exfiltrate.
        /// </summary>
        Exfiltration = 1024,

        /// <summary>
        /// The command and control tactic represents how adversaries communicate with systems under their control within a target network.
        /// </summary>
        CommandAndControl = 2048,

        /// <summary>
        /// The impact intent primary objective is to directly reduce the availability or integrity of a system, service, or network; including manipulation of data to impact a business or operational process.
        /// This would often refer to techniques such as ransom-ware, defacement, data manipulation and others.
        /// </summary>
        Impact = 4096,

        /// <summary>
        /// Probing is any attempt to gather information or failed attempt to gain access to a target system prior to exploitation. 
        /// This step is usually detected as an attempt originating from outside the network in attempt to scan the target system to find a way in.
        /// </summary>
        [Obsolete("Deprecated value, please use PreAttack instead", error: false)]
        Probing = 8192 + PreAttack,

        /// <summary>
        /// Exploitation is the stage where an attacker manage to get foothold on the attacked resource. 
        /// This stage is applicable not only for compute hosts, but also for resources such as user accounts, certificates etc..
        /// Adversaries will often be able to control the resource after this stage.
        /// </summary>
        [Obsolete("Deprecated value, please use InitialAccess instead", error: false)]
        Exploitation = 16384 + InitialAccess,

        /// <summary>
        /// Impair Process Control consists of techniques that adversaries use to disrupt control logic and cause determinantal effects to processes being controlled in the target environment.
        /// Targets of interest may include active procedures or parameters that manipulate the physical environment.
        /// These techniques can also include prevention or manipulation of reporting elements and control logic.
        /// </summary>
        ImpairProcessControl = 32768,

        /// <summary>
        /// Inhibit Response Function consists of techniques that adversaries use to hinder the safeguards put in place for processes and products.
        /// This may involve the inhibition of safety, protection, quality assurance, or operator intervention functions to disrupt safeguards that aim to prevent the loss of life, destruction of equipment, and disruption of production.
        /// </summary>
        InhibitResponseFunction = 65536,

        /// <summary>
        /// Reconnaissance consists of techniques that involve adversaries actively or passively gathering information that can be used to support targeting. 
        /// Such information may include details of the victim organization, infrastructure, or staff/personnel. 
        /// </summary>
        Reconnaissance = 131072,

        /// <summary>
        /// Resource Development consists of techniques that involve adversaries creating, purchasing, or compromising/stealing resources that can be used to support targeting. 
        /// Such resources include infrastructure, accounts, or capabilities. 
        /// </summary>
        ResourceDevelopment = 262144,
    }
}
