# Steps to configure Palo Alto Networks NGFW for sending CEF events.

Perform the following steps to configure the Palo Alto Networks firewall for CEF-formatted Syslog events. The PAN-OS Administrator’s Guide provides additional information about Syslog configuration. Please refer to the [latest PAN-OS Administrator’s Guide](https://docs.paloaltonetworks.com/pan-os/10-0/pan-os-admin) to ensure that you have configured log forwarding correctly for all the log types that you would like to forward to Sentinel platform. 



1. >  To configure the device to include its IP address in the header of Syslog messages, select **Panorama/Device > Setup > Management**, click the Edit icon in the **Logging and Reporting Settings** section and navigate to the **Log Export and Reporting tab**. In the Syslog HOSTNAME Format drop-down select **ipv4-address or ipv6-address**, then click **OK**. 

2. >	Select **Device > Server Profiles > Syslog** and click **Add**. 

3. >	Enter a server profile **Name** and **Location** (location refers to a virtual system, if the device is enabled for virtual systems).

4. >	In the **Servers** tab, click **Add** and enter a **Name**, IP address (**Syslog Server** field), **Transport**, **Port** (default 514 for UDP), and **Facility** (default LOG_USER) for the Syslog server. 

5. >	Select the **Custom Log Format** tab and click any of the listed log types (Config, System, Threat, Traffic, URL, Data, WildFire, Tunnel, Authentication, User-ID, HIP Match) to define a custom format based on the CEF for that log type.

6. > Modify the default CEF header format to make sure we always have 7 fields in CEF header as Sentinel log analytics agent can only parse fixed header (7 fields in header)
```a. > For example, log types “Global Protect” have only 6 fields, and SCTP only have 5 fields in the default configuration. We can introduce dummy fields to make sure we have 7 fields```

7. >	Click OK twice to save your entries, then click Commit
