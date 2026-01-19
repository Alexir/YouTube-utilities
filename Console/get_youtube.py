# find a token or ask the user for an auth
# set up for youtube api
# [20251202] (air)
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

# Here we are telling HTTP Transport Library not to retry the video upload.
httplib2.RETRIES = 1
# MAX_RETRIES specifies the maximum number of retries that can done before giving up.
MAX_RETRIES = 10


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
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
            print(credentials.to_json(),file=sys.stderr )

    # Create a service instance
    youtube = googleapiclient.discovery.build(  api_service_name, api_version, credentials=credentials )

    return(youtube)

# This method implements an exponential
# backoff strategy to resume a failed upload.
def resumable_upload(request, resource, method):
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print("Uploading the file...", file=sys.stderr)
            status, response = request.next_chunk()
    
            if response is not None:
                if method == 'insert' and 'id' in response:  print(response)
                elif method != 'insert' or 'id' not in response:  print(response, file=sys.stderr)
                else:
                    exit("The file upload failed with an unexpected response: % s" % response)
            
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error % d occurred:\n % s"                 % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:  error = "A retriable error occurred: % s" % e
        if error is not None:  print(error, file=sys.stderr)
        retry += 1
    
        if retry > MAX_RETRIES:  exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print(("Sleeping % f seconds and then retrying..."  % sleep_seconds), file=sys.stderr)
        time.sleep(sleep_seconds)
    

# Build a resource based on a list of 
# properties given as key-value pairs.
# Leave properties with empty values 
# out of the inserted resource.
def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split
        # into "snippet" and "title", where
        # "snippet" will be an object and "title" 
        # will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]
    
            # For properties that have array values,
            # convert a name like "snippet.tags[]" to 
            # snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True
    
            if pa == (len(prop_array) - 1):
                # Leave properties without values 
                # out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title",
                # but the resource does not yet have a "snippet"
                # object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next
                # time through the "for pa in range ..." loop,
                # we will be setting a property in the
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

# make a unique playlist name (not a great idea in production)
#    now = datetime.now()
#    title = "title_"+now.strftime("%Y-%m-%d %H:%M:%S")

# prelinary version
#def playlist_insert_item_x(  youtube, playlist = None, video = None, ) :
#    response = youtube.playlistItems().insert(
#        body=resource,
#        **kwargs)
#    response = request.execute()


###########################################
### DEFINE API CALLS
###

#

## INSERT VIDEO
def videos_insert(client, properties, media_file, **kwargs):
    resource = build_resource(properties) 
    kwargs = remove_empty_kwargs(**kwargs) 
    request = client.videos().insert(
        body = resource,
        media_body = MediaFileUpload(media_file, chunksize =-1, resumable = True),
        **kwargs
    )
    return resumable_upload(request, 'video', 'insert')

# VIDEO METADATA
def video_list_details( video_Id) : 
    list_videos_byid = youtube.videos().list(id = video_id,
                                             part = "id, snippet, contentDetails, statistics",
                                               ).execute()

    results = list_videos_byid.get("items", [])  # extract results from search response

    videos = []
    for result in results:
        videos.append("(% s) (% s) (% s) (% s) (% s) (% s)" % (result["snippet"]["title"],
                                                              result["snippet"]["tags"],
                                                              result['snippet']['description'],
                                                              result["snippet"]["publishedAt"],
                                                              result['contentDetails'], 
                                                              result["statistics"]))
    print("Videos:\n", "\n\n".join(videos), "\n")



# INSERT A NEW PLAYLIST; should warn about duplicates
def playlist_insert(client, properties, **kwargs):
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlists().insert( body=resource, **kwargs ).execute()
    
    return print_response(response)


def insert_playlist_x(  # old version
        youtube,
        title="test_playlist",
        description="description stub",
        tags=["#tag1","#tag2"],  # isn't used ... add tags to description
        status="private",
) :

    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title":       title,
                "description": description,
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": status,
            }
        }
    )
    response = request.execute()
    return( response["id"],response["snippet"]["title"],response["status"] )
    


def print_response(response):  print(response)


if __name__ == "__main__":
    
#### TEST FUNCTIONS ####
    
    print("SPAWN A CLIENT")
    service = get_youtube()

    print("INSERT A VIDEO")
    from apiclient.http import MediaFileUpload
    media_file = "geeks_code/videoplayback.mp4"
    response = videos_insert(service, 
                  {'snippet.categoryId': '27',
                   'snippet.defaultLanguage': '',
                   'snippet.description': 'Sample Learn ABC Video',
                   'snippet.tags[]': '',
                   'snippet.title': 'Sample Test video upload',
                   'status.embeddable': '',
                   'status.license': '',
                   'status.privacyStatus': 'private',
                   'status.publicStatsViewable': ''},
                  media_file,
                  part ='snippet, status' )
    video_insert_results = video_insert_response.get("items", [])
    video_inserted = video_insert_results["id"]

    
    print("PLAYLIST_INSERT")
    response = playlist_insert(service,
                               {'snippet.title':'Information Security',
                                'snippet.description':'This playlist contains videos related to \
                                Information Security and Privacy and Security in Online Social Media',
                                'snippet.tags[]':'',
                                'snippet.defaultLanguage':'EN',
                                'status.privacyStatus':''},
                               part='snippet,status',
                               onBehalfOfContentOwner='')
    print(json.dumps(response))


    
    print("SHOW INFORMATION FOR A VIDEO")
    response = video_details(video_inserted)
    video_response = reponse.get("items", [])
    video_inserted = video_response["id"]
 
    print("SHOW PLAYLIST ITEMS")
    # CAUTION: you actaully need to wait for the vid to be processed and available
    # you can do a time.sleep(n), or just skip this bit (n=seconds)
    request = service.playlistItems().list(
        part= "snippet, contentDetails",
        playlistId="PLWbKjPrSYxf6Fqf0HJXPf9c_d97Z2_kZ4",
        maxResults=25,
    )
    response = request.execute()
    print(json.dumps(response))

    #    (id, title, status) = playlist_insert(service)
    #    print(f"{id}\t{title}\t{status}")
       


#

