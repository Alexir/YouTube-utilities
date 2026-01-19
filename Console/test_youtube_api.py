# run tests over the get_youtube module
# the individual sections should be wrapped up; for now copy into your code
# [20251205] (air)
#

"""
You need at least two tests: test_youtube_1.py and test_youtube_2.py. 
Video insertion takes time, so testing can't be a straight-through suite.
It's not clear how long it takes a vid to appear; it may be load depended.
You  need a test_youtube_cleaup.py to remove all the junk you created.
and which would tests delete functions.
If you're not anxious, you can writea  script with sleep() in it.

A good amount of the code is taken from: 
https://www.geeksforgeeks.org/python/youtube-data-api-playlist-set-2/;
that probably should be ".../set-n/", where n is 1..4.
Note that the posted code had issues, most notably messed-up indentation. 
It's a set of one-off demos; the current code adds a persistent token.

This code should give you all you need to deal with vids and playlists.
But it lacks a db, or such, that lets you manage large collections.


youtube_do --tasks "T1,T2,T3,..."  [--video <video_id>] [--playlist <playlist_id>]

    --tasks -- which task to perform and in what order; variable can be set and passed on
    --media -- the video you want to upload

    --title "title"
    --description "description"

useful: TASK sets
    "VIDEO_INSERT_VIDEO, "VIDEO_INSERT_PROGRESS", "VIDEO_DETAILS", ["PLAYLIST_ITEM_INSERT"] 
    "PLAYLIST_INSERT"
   "GET_USER_CHANNEL", "PLAYLIST_ITEMS" 

"""

#
import os, sys

import google_auth_oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import httplib2
#
import googleapiclient.discovery
import googleapiclient.errors

import time
from datetime import datetime,timedelta
import isodate
import random
import json
import argparse
import csv
from io import StringIO


from youtube_core import *



#############################################################################
### DEFINE API CALLS
###

# GET USER'S CHANNEL
def get_user_channel() :
    request = client.channels().list( part="snippet, contentDetails,statistics",  mine=True )
    response = request.execute()
    user_channel = response['items'][0]['id']   # put into global var
    


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

# VIDEO_QUERY_PROGRESS
def video_query_progress( video_Id ) :
    """
    failed – Video processing has failed. See ProcessingFailureReason.
    processing – Video is currently being processed. See ProcessingProgress.
    succeeded – Video has been successfully processed.
    terminated – Processing information is no longer available.
    """
    request = client.videos().list(  part='processingDetails, status',  id=video_Id,  )
    response = request.execute()
    return(response)

# VIDEO DETAILS METADATA
def video_details( client,video_Id) : 
    response = client.videos().list(id = video_Id,
                                             part="id, snippet, contentDetails, statistics",
                                               ).execute()

    return(response)  #  an array
    results = response.get("items", [])  # extract results from search response

#    videos = []
#    for result in results:
#        videos.append("(% s) - (% s) (% s) (% s) (% s)" % (result["snippet"]["title"],
#        videos.append("(% s) (% s) (% s) (% s) (% s) (% s)" % (result["snippet"]["title"],
#                                                              result["snippet"]["tags"],
#                                                              result['snippet']['description'],
#                                                              result["snippet"]["publishedAt"],
#                                                              result['contentDetails'], 
#                                                              result["statistics"])
#                      )
#    print("Videos:\n", "\n\n".join(videos), "\n")
#    return(result[0])




# GET ALL VIDEOS IN USER ACCOUNT
# https://chatgpt.com/c/693c9c3f-e6c8-8329-a7d3-82ea9b7180e8
"""
make a python program, using youtube data api 3 for current user:
get all video. for each video list: id, title, description, tags,
privacy status, selfDeclaredMadeForKids, duration, creationTime,
viewCount, likeCount, commentCount. The listing is over multiple
pages; make sure you get all of them.

"""
def get_all_user_videos(youtube):
    videos = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="id",
            forMine=True,
            type="video",
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        video_ids = [
            item["id"]["videoId"]
            for item in response.get("items", [])
        ]

        if video_ids:
            videos.extend(get_video_details(youtube, video_ids))

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def get_video_details(youtube, video_ids):
    request = youtube.videos().list(
        part="snippet,contentDetails,status,statistics",
        id=",".join(video_ids),
        maxResults=50
    )
    response = request.execute()

    results = []

    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        status = item.get("status", {})
        stats = item.get("statistics", {})

        duration_iso = content.get("duration")
        duration_seconds = (
            int(isodate.parse_duration(duration_iso).total_seconds())
            if duration_iso else None
        )

        video_info = {
            "id": item.get("id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "tags": snippet.get("tags", []),
            "privacyStatus": status.get("privacyStatus"),
            "selfDeclaredMadeForKids": status.get("selfDeclaredMadeForKids"),
            "duration": duration_seconds,
            "creationTime": snippet.get("publishedAt"),
            "viewCount": stats.get("viewCount"),
            "likeCount": stats.get("likeCount"),
            "commentCount": stats.get("commentCount"),
        }

        results.append(video_info)

    return results



#### ---------------------------------------------------------------------------------------
# INSERT a new PLAYLIST; should warn about duplicates...
def playlist_insert(client, properties, **kwargs):
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.playlists().insert( body=resource, **kwargs ).execute()
    
    return print_response(response)

# DELETE a PLAYLIST
def delete_playlist( playlist_Id ) : 
    if verbose : print("DELETE PLAYLIST:", playlistId)
    response = playlist_delete( playlistId )

# DELETE VIDEO from playlist
def video_delete( client,video_Id ) :
    request = client.playlists().delete( id=video_Id ) 
    response = request.execute()
    return response
    


#### -----------------------------------------------------------------------------------------
def parse_csv_string(s):
    """Parse a CSV-like string into a list of values.
    Handles quoted values that may contain commas or spaces.
    Quotes are removed from quoted values.
    """
    # Use csv.reader to properly handle quoted strings
    reader = csv.reader(StringIO(s), skipinitialspace=True)
    result = next(reader)
    
    return result


#############################################################################
if __name__ == "__main__":
        
    # useful globals,  meant to persist and be used over tasks
    user_channel   = ''
    media_file = ''   # use 
    video_inserted = ''
    target_playlist = ""
    target_channel = user_channel
    #    video_inserted = "r09VjjRAnCo"   #  "coal country cloggers "

    # parse cli items
    parser = argparse.ArgumentParser(description="Access to YouTube API")
    parser.add_argument( '--tasks', required=True, help="sequential list of tasks to perform",
                         const=None, default=None, nargs='?'  )
    parser.add_argument( '--playlist', help='playlist to insert/delete, or where to add video' )
    parser.add_argument( '--video', help='item to playlist_item_insert, delete, video_details' )
    parser.add_argument( '--media', help='video file to upload' )
    parser.add_argument( '-v','--verbose', action="store_true" )
    args = parser.parse_args()
    if args.verbose : verbose = True
    else: verbose = False
    
    if args.playlist != None : target_playlist = args.playlist   # new to make, or existing
    if args.video != None : video_inserted = args.video  # an existing item ID
    media_file = "geeks_code/videoplayback.mp4"      #  a dummy file, for testing
    if args.media != None : media_file = args.media   # a new upload (an ID is returned)
    


    ######## TEST FUNCTIONS ###################################################################

    ## -------------------------
    if verbose : print("SPAWN A CLIENT", file=sys.stderr)
    client = get_youtube()
    if verbose : print()

    # which tasks to perform; a comma-delimited list in --tasks
    TASK_SET = [ "VIDEO_INSERT",
                 "VIDEO_DELETE",
                 "VIDEO_DETAILS",
                 "VIDEO_INSERT_PROGRESS",
                 "VIDEO_LIST_ALL",
                 
                 "PLAYLIST_INSERT",
                 "PLAYLIST_DELETE",
                 "PLAYLIST_INSERT_ITEMS",
                 "PLAYLIST_LIST_ITEMS",
                 "PLAYLIST_LIST_ALL",
                 
                 "GET_USER_CHANNEL",
                 "SEARCH",
                ]
    
    # which to do on this run; order matters
    # this should be for the CLI... items executed in sequence given
    #    TASKS = [ "INSERT_VIDEO","VIDEO_DETAILS", "VIDEO_INSERT_PROGRESS" ]

    if args.tasks == None :
        print("specify one or more of these TASKS: (order-sensitive)\n"+'\n'.join(TASK_SET))
        sys.exit()

    TASKS = [ "GET_USER_CHANNEL", ]  # a stub
    task_list = parse_csv_string(args.tasks)   # expand tasks into a list
    for i in task_list :
        if verbose : print("doing: ",i)
        TASKS = [ i ]   # hack...


        ## -------------------------
        if "VIDEO_INSERT" in TASKS :
            if verbose : print("INSERT A VIDEO", file=sys.stderr)
            from apiclient.http import MediaFileUpload
            # media_file = "geeks_code/videoplayback.mp4"  # used for testing
            if media_file == None :
                print("you didn't specify a media file!",file=sys.stderr)
                sys.exit()
            response = videos_insert(client, 
                                     { # see https://mixedanalytics.com/blog/list-of-youtube-video-category-ids/
                                         'status.selfDeclaredMadeForKids': "False",
                                         
                                         'snippet.categoryId': '27',  # "education"
                                         'snippet.defaultLanguage': 'EN',  # assumed...
                                         'snippet.description': 'Sample Learn ABC Video',  # SHOULD have
                                         'snippet.tags[]': '',
                                         'snippet.title': 'Sample Test video upload',  # MUST have
                                         
                                         'status.embeddable': '',
                                         'status.license': '',  # CC?
                                         'status.privacyStatus': 'private',  # remember to change when ready
                                         'status.publicStatsViewable': '',
                                     },
                                     media_file,  # MUST have
                                     part ='snippet, status'
                                     )

            # check up on progress; won't be ready, but gives estmated time
            video_inserted = response["id"]
            if verbose : print("Inserting:\t", video_inserted, file=sys.stderr )
            continue
            
        ## -------------------------
        if "VIDEO_INSERT_PROGRESS" in TASKS : 
            if verbose : print( "VIDEO_INSERT_PROGRESS", file=sys.stderr )

            continue


        ## -------------------------
        if "INSERT_PLAYLIST" in TASKS : 
            if verbose : print("PLAYLIST_INSERT", file=sys.stderr)
            response = playlist_insert(client,
                                       {'snippet.title':target_playlist,
                                        'snippet.description':'This playlist contains videos related to stuff',
                                        'snippet.tags[]':'',
                                        'snippet.defaultLanguage':'EN',
                                        'status.privacyStatus':''},
                                       part='snippet,status',
                                       )
            #  print(json.dumps(response))
            continue


    
        ## -------------------------
        if "VIDEO_DETAILS" in TASKS :
            if verbose : print("VIDEO_DETAILS: show information for a video")
            #        video_inserted = "r09VjjRAnCo"  # "Coal Country Cloggers"
            response = video_details(client, video_inserted)
            vid = response.get("items", [])[0]   # look at only the first item in returned array
            
            print( 'Id:\t',vid["id"])
            snippet = vid["snippet"]
            keys = snippet.keys()
            print( f"title:\t{snippet['title']}", end="\n")
            if 'tags' in keys : print( f"tags:\t{snippet['tags']}", end="\n" )
            print( f"descr:\t{snippet['description']}",  end="\n")
            print( f"pubDate\t{snippet['publishedAt']}", end="\n")
            print( f"id:\t{snippet['categoryId']}",      end="\n")

            continue
            
            
        ## -------------------------
        if "VIDEO_LIST_ALL" in TASKS :
            if verbose : print("VIDEO_LIST_ALL: show information for all  videos in account", file=sys.stderr)
            videos = get_all_user_videos( client )
            print( "found: ",len(videos)," videos", file=sys.stderr )

            with open('playlist.csv','w',newline='', encoding='utf-8' ) as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow( ['id','status','count','duration','title','tags'] )
                for v in videos :
                    if v['privacyStatus'] == 'private' : status = ' -- '
                    elif v['privacyStatus'] == 'public' : status = 'PUBL'
                    elif v['privacyStatus'] == 'unlisted' : status = 'unli'
                    if v['viewCount'] == '0' : count='-'
                    else: count = v['viewCount']
                    dur = str(timedelta(seconds=v['duration']))
                    print(f"{v['id']}\t{status[:4]} {count:>4}  {dur}\t{v['title']}|--> {v['tags']}" )
                    writer.writerow([v['id'], status,count,dur, v['title'], v['tags']] )
                                 

            print( '---', len(videos), " videos", file=sys.stderr )
            
            continue

        ## -------------------------
        if "PLAYLIST_LIST_ITEMS"  in TASKS :
            if verbose : print("PLAYLIST ITEMS: listing of videos in a playlist", file=sys.stderr)
            # CAUTION: you actually need to wait for the vid to be processed and available
            # you can do a time.sleep(n), or just skip this bit (n=seconds)
            request = client.playlistItems().list(
                part= "snippet, contentDetails",
                playlistId=target_playlist,  # from global var
                maxResults=25,  )
            response = request.execute()
            if verbose : print(json.dumps(response), file=sys.stderr)
            
            # for each item ion the playlist, determine if it's still live
            # playlist need vids to be active and to be listed for the user.
            video_items = []
            newPToken = None
            while True :
                if newPToken :  # is this a long(er) list?
                    request = client.playlistItems().list(
                        part = "snippet, contentDetails",
                        playlistId = target_playlist,
                        maxResults=25,
                        pageToken = newPToken,
                    )
                else:   # fewer than maxResults
                    request = client.playlistItems().list(
                        part = "snippet, contentDetails",
                        playlistId = target_playlist, 
                        maxResults=25, 
                    )
                response = request.execute()  # get the list of vids in playlist
                    
                # add results to video list and (maybe) look for more
                video_items.extend( response.get("items", []) )
                if "nextPageToken" in response.keys() :
                    newPToken = response["nextPageToken"]
                else:
                    break
            # end while loop
            
            # print all videos in this playlist
            if len(video_items) > 0 :
                for item in video_items : 
                    video_title = item["snippet"]["title"]
                    video_id = item["contentDetails"]["videoId"]
                    print(f"{target_playlist}\t{video_id}\t \"{video_title}\"")
                print( "--- ",len(video_items),"videos", file=sys.stderr )
            else:
                print("--- no vids", file=sys.stderr)

            continue
            
            
        ## -------------------------
        if "DELETE_VIDEO" in TASKS :
            video_Id = video_inserted
            #        video_Id = ""
            if verbose : print("DELETE VIDEO:", video_Id , file=sys.stderr)
            video_delete( client, id=video_Id )
            continue
                
        ## -------------------------
        if "DELETE_PLAYLIST" in TASKS :
            # playlist_Id = ""
            if verbose : print("DELETE PLAYLIST:", playlist_Id, file=sys.stderr )
            playlist_delete( target_playlist )
            continue
            
        ## -------------------------
        if "GET_USER_CHANNEL" in TASKS :
            request = client.channels().list( part="snippet, contentDetails,statistics",  mine=True )
            response = request.execute()
            user_channel = response['items'][0]['id']   # put into global var
            print( "--- user channel: ", user_channel, file=sys.stderr )
            continue
                        
        ## -------------------------
        if "PLAYLIST_LIST_ALL" in TASKS :
            if verbose : print( "PLAYLIST_LIST_ALL: list all playlists in the account channel", file=sys.stderr  )
            # get the list of lists (i.e. top level channel in the account)
            request = client.playlists().list(  part= "snippet, contentDetails",
                                                mine = True,  # own account (@AlexanderRudnicky in our case)
                                                maxResults = 100,  ) # should do dynamic list,  like for below
            response = request.execute()
            
            playlist_list = response.get("items", [])
            for playlist_item in playlist_list :
                playlist_id = playlist_item["id"]
                title = playlist_item["snippet"]["title"]
                channelId = playlist_item["snippet"]["channelId"]
                count = playlist_item['contentDetails']['itemCount']
                description = playlist_item["snippet"]["localized"]["description"]

                
                print( f"{playlist_id}\t{count:4d}\t\"{title}\"\t\"{description}\"")   ## \t {channelId}" )
                
            if verbose : print( '---', len(playlist_list), " playlists" , file=sys.stderr )
            continue
            

        ## -------------------------
        # --tasks item not found, flag and keep going
        print("\n*** unknown task:",i, "  *** quitting!", file=sys.stderr )
        break


    
print( "\nDone", file=sys.stderr )

#
