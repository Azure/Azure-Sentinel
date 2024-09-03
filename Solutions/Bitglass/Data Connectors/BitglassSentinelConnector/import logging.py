import requests

bitglass_serviceURL = "https://portal.eu.bitglass.net"
event_type = "swgweb"
url = f'{bitglass_serviceURL}/api/bitglassapi/logs/v1/'
bearer_token = "vm0QtGXJITtHBo4NcZZa8j8vJUiRf2"
token = None
from_time = "2024-09-02T09:50:14Z"
headers = {
       "Authorization": f"Bearer {bearer_token}",
       "Content-Type": "application/json"
   }

adapter = requests.adapters.HTTPAdapter
session = requests.Session()
session.mount('https://', adapter)
if token is None:
            params = {
                "startdate": from_time,
                "cv": "1.0.1",
                "type": event_type,
                "responseformat": "json"
            }

            r = requests.get(url=url,
                             headers=headers,
                             params=params
                             )
            if r.status_code == 200:
                print(r.json())
            elif r.status_code == 401:
                print("The authentication credentials are incorrect or missing. Error code: {}".format(
                    r.status_code))
else:
            params = {
                "nextpagetoken": nextpagetoken,
                "cv": "1.0.1",
                "type": event_type,
                "responseformat": "json"
            }

            r = requests.get(url=url,
                            headers=headers,
                            params=params
                            )
            if r.status_code == 200:
                print(r.json())
            elif r.status_code == 401:
                print("The authentication credentials are incorrect or missing. Error code: {}".format(
                    r.status_code))
response = requests.get(url, headers=headers)
       
if response.status_code == 200:
           logs = response.json()
           print (logs)

# ================================================================================================

# import requests



# headers = {
#        'Authorization': f'Bearer {bearer_token}',
#        'Content-Type': 'application/json'
#    }
# logs = []
# next_page_token = None
# while True:
#        # Prepare the request URL with the next page token if it exists
#        url = api_url
#        if next_page_token:
#            url = f"{api_url}?nextPageToken={next_page_token}"
#        response = requests.get(url, headers=headers)
#        if response.status_code == 200:
#            data = response.json()
#            # Add the logs from the current response
#            logs.extend(data.get('logs', []))
#            # Check for the next page token
#            next_page_token = data.get('nextPageToken')
#            # If there's no next page token, break the loop
#            if not next_page_token:
#                break
#        else:
#            # Handle potential errors
#            print(f"Error: {response.status_code} - {response.text}")
#            break
# print(logs)

           