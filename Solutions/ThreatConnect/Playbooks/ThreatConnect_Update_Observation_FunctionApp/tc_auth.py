import os

from tc_session import TcSession
from hmac_auth import HmacAuth

tc_base_url = os.environ.get("TC_BASE_URL", None)
tc_api_access_id = os.environ.get("TC_API_ACCESS_ID", None)
tc_api_secret_key = os.environ.get("TC_API_SECRET_KEY", None)

tc_api_endpoint = os.environ.get("TC_API_ENDPOINT", "/api/v3/groups")

sesh = TcSession(
    HmacAuth(tc_api_access_id, tc_api_secret_key),
    base_url=tc_base_url,
    verify=False,
)
response = sesh.get(tc_api_endpoint)
print(response.json())
