# run tests over the get_youtube module
# [20251205] (air)
#

"""
You need at least two test sets: test_youtube_1.py and test_youtube_2.py. 
Video insertion takes time, so testing can't be a straight-through suite.
It's not clear how long it takes a vid to appear; it may be load depended.
You  need a test_youtube_cleaup.py to remove all the junk you created.
and which would also test delete functions.
If you're not anxious, you could write a script with sleep() in it.

A good amount of the code is taken from Rashi Garg's
https://www.geeksforgeeks.org/python/youtube-data-api-playlist-set-2/ 
(which probably should be ".../set-n/", where n is 1..4).
Note that their posted code had issues, most notably messed-up indentation. 
It's a set of one-off demos; the current code adds a persistent token.

This code should give you all you need to play with vids and playlists.
But it lacks a db, or such, that lets you manage large collections.

"""
#


import os

import google_auth_oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import httplib2
#
import googleapiclient.discovery
import googleapiclient.errors

import time
from datetime import datetime
import random
import json

httplib2.RETRIES = 1  # tell the HTTP Transport Library not to retry the video upload.
MAX_RETRIES = 10      # the maximum number of retries that can done before giving up.


# spawn an instance of the youtube client; checkl if we already have a token
def get_youtube(secret="credentials.json",
              token="token.json",
              scopes=[
                   "https://www.googleapis.com/auth/youtube.force-ssl",
              ]) :

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
        # If there are no (valid) credentials available, make the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file( "credentials.json", scopes )
            credentials = flow.run_local_server(port=0)
            # Save these credentials for the next run
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
            print(credentials.to_json())

    # Create a service instance
    youtube = googleapiclient.discovery.build(  api_service_name, api_version, credentials=credentials )

    return(youtube)

# This method implements an exponential backoff strategy to resume a failed upload.
def resumable_upload(request, resource, method):
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print("Uploading the file...")
            status, response = request.next_chunk()
    
            if response is not None:
                if method == 'insert' and 'id' in response:  pass   # print(response)
                elif method != 'insert' or 'id' not in response:  print(response)
                else:
                    exit("The file upload failed with an unexpected response: % s" % response)
            
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error % d occurred:\n % s"  % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:  error = "A retriable error occurred: % s" % e
        if error is not None:  print(error)
        retry += 1
    
        if retry > MAX_RETRIES:  exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print(("Sleeping % f seconds and then retrying..."  % sleep_seconds))
        time.sleep(sleep_seconds)

        return(response)

    
# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]
    
            # For properties that have array values, convert a name like "snippet.tags[]" to 
            # snippet.tags, and set a flag to handle the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True
    
            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title",
                # but the resource does not yet have a "snippet" object.
                # Create the snippet object here. Setting "ref = ref[key]" means that in the next
                # time through the "for pa in range ..." loop,  we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description",
                # and the resource already has a "snippet" object.
                ref = ref[key]
    return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs





if __name__ == "__main__":
    print("--> see tests in: test_youtube_api.py")
    
    #### TESTS ARE IN SEPARATE FILES ####
    # test_youtube_api_1.py
    # test_youtube_api_2.py
    # test_youtube_api_cleanup.py
    

#
    
    
