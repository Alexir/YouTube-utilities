# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python
 
 # xchange
 
import os
import json

import google_auth_oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
#
import googleapiclient.discovery
import googleapiclient.errors

from get_youtube import get_youtube


def main() :
    
    youtube = get_youtube(secret="credentials.json")
    
    
    # get the list of lists
    request = youtube.playlists().list(
        part= "snippet, contentDetails",
        maxResults = 100,  # should do dynamic list,  like below
#        forHandle= "@AlexanderRudnicky",
        mine=True,  # own account (@AlexanderRudnicky in our case)
    )
    response = request.execute()
    
    print("---")
    playlist_list = response.get("items", []) 
    for playlist_item in playlist_list :
        playlist_id = playlist_item["id"]
        title = playlist_item["snippet"]["title"]
        channelId = playlist_item["snippet"]["channelId"]
        print( f"\n--- playlist: {playlist_id}\t\"title\": {title}\tchannelId: {channelId}" )

        # for each item ion tyhe playlist, determine if it's still live
        # playlist need vids to be active and to be listed for the user.
        video_items = []
        newPToken = None
        while True :
            if newPToken :  # is this a long(er) list?
                request = youtube.playlistItems().list(
                    part = "snippet, contentDetails",
                    playlistId = playlist_item["id"],
                    maxResults=25,
                    pageToken = newPToken,
                )
            else:   # fewer than maxResults
                request = youtube.playlistItems().list(
                    part = "snippet, contentDetails",
                    playlistId = playlist_item["id"],
                    maxResults=25, 
                )
            response = request.execute()  # get the list of vids in playlist
            
            # add to video list and (maybe) look for more
            video_items.extend( response.get("items", []) )
            if "nextPageToken" in response.keys() :
                newPToken = response["nextPageToken"]
                # print ( "nextPageToken: ", newPTok )
            else:
                break
            
        # list all videos in this playlist
        print("--- playlist\tvideoId\t video_title")
        if len(video_items) > 0 :
            for item in video_items : 
                video_title = item["snippet"]["title"]
                video_id = item["contentDetails"]["videoId"]
                print(f"{playlist_id}\t{video_id}\t \"{video_title}\"")
            print( "--- ",len(video_items),"videos" )
        else:
            print("--- no vids")
        
    
# dump the respose
    
    data = json.dumps(response,indent=2)
    with open("data.json", "w") as out :
            out.write(data)
#    print(data)
    print("done")
#    print(
#        data["items"]["etag"],"\n",
#        )


if __name__ == "__main__":
    main()

