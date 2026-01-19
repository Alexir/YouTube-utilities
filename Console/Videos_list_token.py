# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python


# change

import os

import google_auth_oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
#
import googleapiclient.discovery
import googleapiclient.errors


SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version      = "v3"
    client_secrets_file = "credentials.json"
    token_file = "token.json"
    credentials = None
    
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
            print(credentials.to_json())



    # Get credentials and create an API client
    #flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #    client_secrets_file, SCOPES)
    #    credentials = flow.run_console()   # doesn't work from wsl ubuntu shell
    #credentials = flow.run_local_server(port=0) # ,open_browser=False)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part= "snippet, contentDetails, statistics",
        id="Ks-_Mh1QhMc"
#        part= "snippet, id=PLWbKjPrSYxf6Fqf0HJXPf9c_d97Z2_kZ4"
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()

