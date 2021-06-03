import pickle
import os.path
import base64

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        print("There is no token.pickle file. Please check.")
        exit(0)
    print("\n\nCopy pickle string and save. Paste it during installation GWorkspace Function App:\n\n{}".format(base64.b64encode(pickle.dumps(creds))))
if __name__ == '__main__':
    main()