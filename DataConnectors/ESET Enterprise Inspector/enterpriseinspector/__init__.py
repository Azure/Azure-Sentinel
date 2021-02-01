import requests

from enterpriseinspector.enterpriseinspector import EnterpriseInspector
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable default SSL warning 
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
