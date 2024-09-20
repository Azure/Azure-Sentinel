# Send Email Warning when email:password combination is received from Firework identifiers alerts
Author: Jean-Christophe, Flare Systems

This playbook monitors all data received from Firework looking for leaked credentials (email:password combinations). When found, this playbook will send an email to the email address warning their password has been leaked, recommending appropriate measures if necessary. To learn more about how to connect Firework to Microsoft Sentinel, see the [API documentation](https://docs.flared.io/azure-sentinel-integration).

<a href="" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>