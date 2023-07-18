import os

from dotenv import load_dotenv

load_dotenv()

API_KEY= os.getenv('API_KEY')
API_SECRET= os.getenv('API_SECRET')
BASE_URL = os.getenv('BASE_URL', 'https://api.mailrisk.com/v1/')

# Log Analytics workspace ID
WORKSPACE_ID=os.getenv('WORKSPACE_ID')
# Primary or secondary Connected Sources client authentication key   
WORKSPACE_KEY=os.getenv('WORKSPACE_KEY')
# The log type is the name of the event that is being submitted
LOG_TYPE=os.getenv('LOG_TYPE', 'MailRiskEmails')

VERIFY_CERTIFICATE = (os.getenv('VERIFY_CERTIFICATE', 'True') == 'True')
