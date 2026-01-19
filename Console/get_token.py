# find a token or ask the user for an auth
# set up for youtube api
# [20251202] (air)
#

import os

import google_auth_oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
#
import googleapiclient.discovery
import googleapiclient.errors

def get_youtube(secret="credentials.json",
              token="token.json",
              scopes=["https://www.googleapis.com/auth/youtube.readonly"]) :

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version      = "v3"
    client_secrets_file = secret
    token_file = token
    credentials = None
    
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", scopes)
        # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scopes
            )
            credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
            print(credentials.to_json())

    # Create a service instance
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    return(youtube)

if __name__ == "__main__":
    print("If this worked, you'll get an object:")
    service = get_youtube()
    print(service)

#

