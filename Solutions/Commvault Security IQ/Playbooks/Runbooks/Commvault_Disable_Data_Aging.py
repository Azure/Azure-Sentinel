import requests
import sys

# Suppress only the InsecureRequestWarning from urllib3 needed for ignoring SSL warnings
requests.packages.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)


# Declare Variables
print("Reading Variables")
apiAccessToken = sys.argv[1]
clientName = sys.argv[2]
EnvironmentEndpointURL = sys.argv[3]

print(clientName)
print(EnvironmentEndpointURL)
print(apiAccessToken)

# Global Variables
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authtoken": f"QSDK {apiAccessToken}"
}

# Get all Tenant Clients
get_clients_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/client"
get_clients_result = requests.get(get_clients_url, headers=headers, verify=True)

if get_clients_result.status_code == 200:
    try:
        res = get_clients_result.json()
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        exit()
else:
    print(f"Error: {get_clients_result.status_code} - {get_clients_result.text}")
    exit()

# Add wildcard (on the end) to Server Input
print(clientName)
print(res)


# Select all Clients that match Input Server Hostname or ClientName
selected_clients = []
for clients in res["clientProperties"]:
    client = clients["client"]["clientEntity"]
    if client["hostName"].startswith(clientName) or client["clientName"].startswith(clientName):
        selected_clients.append({
            "ClientName": client["clientName"],
            "ClientHostname": client["hostName"],
            "ClientID": client["clientId"]
        })

# Check if Clients array is not empty
if selected_clients:
    # Print matched Clients for reference
    print("Following Client(s) were found that match input Server Hostname or ClientName")
    print(selected_clients)
    print("------------------------------")

    # Start flow for each matched Client in array
    for selected_client in selected_clients:
        # Get attributes as ID, ClientName, and Hostname from matched Clients array for the current Client
        selected_client_id = selected_client["ClientID"]
        selected_clientName = selected_client["ClientName"]
        selected_client_hostname = selected_client["ClientHostname"]

        # Get Client Properties and Archive Pruning Status
        get_client_prop_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/client/{selected_client_id}"
        get_client_prop_result = requests.get(get_client_prop_url, headers=headers, verify=True).json()
        client_activity_control_options = get_client_prop_result["clientProperties"][0]["clientProps"]["clientActivityControl"]["activityControlOptions"]
        client_activity_type16_control_options = next((opt for opt in client_activity_control_options if opt["activityType"] == 16), None)
        client_archive_pruning_status = client_activity_type16_control_options.get("enableActivityType", False)

        # Check Archive Pruning Status and perform relevant action
        if client_archive_pruning_status:
            # Archive Pruning is Enabled, Disable it
            body = {
                "clientProperties": {
                    "Client": {"ClientEntity": {"clientId": int(selected_client_id)}},
                    "clientProps": {
                        "clientActivityControl": {
                            "activityControlOptions": [
                                {
                                    "activityType": 16,
                                    "enableAfterADelay": False,
                                    "enableActivityType": False
                                }
                            ]
                        }
                    }
                }
            }
            disable_client_archive_pruning_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/client/{selected_client_id}"
            disable_client_archive_pruning_result = requests.post(disable_client_archive_pruning_url, json=body, headers=headers, verify=True).json()
            disable_client_archive_pruning_result_error_code = disable_client_archive_pruning_result.get("response", {})[0].get("errorCode", None)

            # Check status of operation to Disable Archive Pruning Status and print relevant message
            if disable_client_archive_pruning_result_error_code == 0:
                print(f"Archive Pruning successfully Disabled for Client {selected_clientName} (Hostname: {selected_client_hostname})")
            else:
                print(f"Something went wrong. Error code {disable_client_archive_pruning_result_error_code} does not indicate success for disabling Archive Pruning on Client {selected_clientName} (Hostname: {selected_client_hostname})")
        else:
            # Archive Pruning is already Disabled, print status
            print(f"Archive Pruning is already Disabled for Client {selected_clientName} (Hostname: {selected_client_hostname}). No further action taken.")
else:
    # Clients array is empty, print error message
    print("Something went wrong. No Client(s) found")
