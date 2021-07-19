# Enrich-SentinelIncident-ReversingLabs-File-Information
This playbook utilizes the ReversingLabs Intelligence connector to automatically enrich incident comments section with file information.

Learn more about the integration via the [connector documentation](https://docs.microsoft.com/connectors/reversinglabsintelligence/).

In order to successfully run this playbook you will need a valid ReversingLabs TitaniumCloud subscription with the  XREF(Historic Multi-AV Scan Records), File Reputation and File Hash Analysis Detail APIs enabled. You can obtain your subscription at support@reversinglabs.com.

Playbook extracts hashes (SHA-1, SHA-256 or MD5) by utilizing Azure Sentinel-recognized entity FileHashCustomEntity. In your custom rule, map your hash field to this entity:
```  
 YourLog_CL
    | extend FileHashCustomEntity = <your_hash_field>
```  

Sample comment output:
```
ReversingLabs Multi-AV Scan Records:

ahnlab_online : antivir : detectedavast : Win32:Malware-genbitdefender : carbonblack_online : clamav : PUA.Win.Packer.Exe-6crowdstrike : crowdstrike_online : drweb : Trojan.DownLoader33.21319ensilo_online : esetnod32 : f_prot : fireeye_online : fortinet : gdata : ikarus : invincea_online : k7computing : kaspersky_online : mcafee_online : Artemis!08490DB63F89 (trojan)microsoft_online : panda_online : quickheal : rising_online : Trojan.MalCert!1.C446sentinelone_online : sophos_online : sunbelt : symantec_beta : trendmicro_consumer : vba32 : Trojan.Downloaderwatchguard_online :


ReversingLabs File Hash Details:

This file (SHA1: db2363303dfa061ae92c8e2c114277174c5f5e38) is a 32-bit portable executable application. Additionally, it was identified as InnoSetup installer, and unpacking was successful. The application uses the Windows graphical user interface (GUI) subsystem, while the languages used are Dutch from Netherlands and English from United States. According to version information, this is CoronaVirus Status [Plugin for Google Chrome] from CENTR MBR LLC. Appended data was detected at the file's end. Its length is greater than the size of the image. Cryptography related data was found in the file. This application has access to device configuration, monitoring, networking and running processes and has security related capabilities. The application is digitally signed, and its certificate is valid. There are 874 extracted files.

Sha1: db2363303dfa061ae92c8e2c114277174c5f5e38

Sd5: 08490db63f89b78bdfbc3dd3ae17c706

Sha256: 33cc2944588599a4c70215483e3a59c957c6e7be091a230f9ab9297d12f00933

Sha384: deb41647a35986dff1b82faf8f957a7ab78b98109ca3c7bdb67dd27ec42a9cd26d6f4e5a26e63b716703bd497db70032

Sha512: b015c0ff6efc24a35b954021d8fdb9ab3b7d69cb1314b629607aae197642ab3999a5aa32388708586058ade19d91ec558e6170e42f92c46cafceed54a829dd0e

Sample size: 11135784KB


ReversingLabs File Hash Reputation:

File name: Win32.Trojan.Generic

File status: MALICIOUS

Reason: analyst_sample_override

Scanner count: 31

Scanner percent: 22.5806446075439

Scanner match: 7

First seen: 2020-04-03T06:41:18

Last seen: 2021-02-07T09:45:35

Threat level: 5

Trust factor: 5
```

