import base64
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8081)
    if not creds or not creds.valid:
        print("There is issue with credentials. Please check.")
        exit(0)
    print("\n\nCopy pickle string which is present in single quotes and save. Paste it during installation GWorkspace Function App:\n\n{}".format(base64.b64encode(pickle.dumps(creds))))           

if __name__ == '__main__':
    main()