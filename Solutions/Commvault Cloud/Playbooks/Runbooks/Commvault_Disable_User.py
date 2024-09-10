import requests
import sys

# Suppress only the InsecureRequestWarning from urllib3 needed for ignoring SSL warnings
requests.packages.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

# Declare Variables
print("Reading Variables")
apiAccessToken = sys.argv[1]
userIdentity = sys.argv[2]
EnvironmentEndpointURL = sys.argv[3]

print(userIdentity)
print(EnvironmentEndpointURL)
print(apiAccessToken)

# Global Variables
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authtoken": f"QSDK {apiAccessToken}"
}

# Get all Tenant Users
url = "/commandcenter/api/User?level=10"
get_users_url = f"https://{EnvironmentEndpointURL}{url}"
get_users_result = requests.get(get_users_url, headers=headers, verify=True)

if get_users_result.status_code == 200:
    try:
        res = get_users_result.json()
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        exit()
else:
    print(f"Error: {get_users_result.status_code} - {get_users_result.text}")
    exit()

# Select User based on email or UPN
selected_user_id = "Empty"
selected_user = next((user for user in res["users"] if user["email"] == userIdentity or user["UPN"] == userIdentity), None)
if selected_user:
    selected_user_id = selected_user["userEntity"][0]["userId"]
else:
    print(f"User {userIdentity} was not found")
    exit()

# Get selected user details
get_selected_user_details_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/User/{selected_user_id}"
get_selected_user_details_result = requests.get(get_selected_user_details_url, headers=headers, verify=True)

# Check user if user is enabled and take action
if get_selected_user_details_result.status_code == 200:
    enable_user_status = get_selected_user_details_result.json().get("users", {}).get("enableUser", None)
    if enable_user_status is not None:
        if enable_user_status:
            disable_user_url = f"https://{EnvironmentEndpointURL}/commandcenter/api/User/{selected_user_id}/Disable"
            disable_user_result = requests.put(disable_user_url, headers=headers, verify=True)
            disable_user_result_error_code = disable_user_result.json().get("response", {}).get("errorCode", None)
            if disable_user_result_error_code == 0:
                print(f"User {userIdentity} was successfully disabled")
            else:
                print(f"Something went wrong. Error code {disable_user_result_error_code} for disabling User account {userIdentity} does not indicate success.")
        else:
            print(f"User {userIdentity} is already disabled. No action taken.")
    else:
        print(f"Something went wrong. Cannot retrieve status for user {userIdentity}")
else:
    print(f"Error: {get_selected_user_details_result.status_code} - {get_selected_user_details_result.text}")

