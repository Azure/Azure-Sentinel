import requests
import sys

# Suppress only the InsecureRequestWarning from urllib3 needed for ignoring SSL warnings
requests.packages.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

# Declare Variables
print("Reading Variables")
apiAccessToken = sys.argv[1]
EnvironmentEndpointURL = sys.argv[2]

print(EnvironmentEndpointURL)
print(apiAccessToken)

# Global Variables
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authtoken": f"QSDK {apiAccessToken}"
}

# Get all Tenant Identity Servers
get_identity_servers_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/IdentityServers"
get_identity_servers_result = requests.get(get_identity_servers_url, headers=headers, verify=True)

if get_identity_servers_result.status_code == 200:
    try:
        res = get_identity_servers_result.json()
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        exit()
else:
    print(f"Error: {get_identity_servers_result.status_code} - {get_identity_servers_result.text}")
    exit()

# Filter Identity Servers that are SAML type
saml_identity_servers = [server for server in res["identityServers"] if server["samlType"] == 1]

# For each SAML Identity Server go with steps to check its state and take action
for saml_identity_server in saml_identity_servers:
    # Gets details of SAML Identity Server
    saml_identity_server_name = saml_identity_server["IdentityServerName"]
    getsaml_identity_server_prop_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/V4/SAML/{saml_identity_server_name}"
    getsaml_identity_server_prop_result = requests.get(getsaml_identity_server_prop_url, headers=headers, verify=True)

    # Check if SAML Identity Server is enabled or disabled and take action or give status
    if getsaml_identity_server_prop_result.status_code == 200:
        saml_server_details = getsaml_identity_server_prop_result.json()
        if saml_server_details["enabled"]:
            print(f"Going to disable IDP server {saml_identity_server_name}")
            # Disable SAML Identity Server if it is enabled
            body = {"enabled": False, "type": "SAML"}
            disablesaml_identity_server_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/V4/SAML/{saml_identity_server_name}"
            disablesaml_identity_server_result = requests.put(disablesaml_identity_server_url, json=body, headers=headers, verify=True)
            disablesaml_identity_server_resulterror_code = disablesaml_identity_server_result.json().get("errorCode", None)
            # Based on response error code verify if action was successful and return status
            if disablesaml_identity_server_resulterror_code == 0:
                print(f"SAML IdentityProvider {saml_identity_server_name} successfully disabled")
            else:
                print(f"Something went wrong. Error code {disablesaml_identity_server_resulterror_code} for disabling SAML IdentityProvider {saml_identity_server_name} action does not indicate success")
        else:
            print(f"SAML IdentityProvider {saml_identity_server_name} is already disabled. No action taken")
    else:
        print(f"Something went wrong. Unable to retrieve state for SAML IdentityProvider {saml_identity_server_name}")
