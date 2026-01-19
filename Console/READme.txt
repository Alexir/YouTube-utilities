YouTube API
-----------
[20260103] (air)

files:
test_youtube_api.py -- the main program
get_youtube.py -- support functions.
credentials.jsaon -- your developer credentials

An app that gives you cli access to YouTube.  The main point of this
code is to allow you to intercact with YouTube in batch mode.

You should keep your YouTube credentials in a file "credentials.jon"
in the working directory.  If it's not there it will ask the user to authenticate. 
An url will be printed, which you should cut and paste into a
browser window.  This will give app a token, which it will save and
reuse (if you do things within a certain time limit).
Note that I programmed this as a "developer". You may neeb to be one.
As a developed you can setup a project for an "app" and get credentials.


This code will work in a shell that's not native (like on Windows),
like Git Bash, or Ubuntu.  I haven't done this, but you can probanbly
get this running in a powershell.  Running in a gui sort of defeats
the purpose; just use the YouTube website.

Do help to know the cmd line arguments.
The app should handle all/most of the calls you might need:

# which tasks to perform; a comma-delimited list in --tasks
    TASKS = [ "VIDEO_INSERT",
              "VIDEO_DELETE",
              "VIDEO_DETAILS",
              "VIDEO_INSERT_PROGRESS",
              "VIDEO_LIST_ALL",
              
              "PLAYLIST_INSERT",
              "PLAYLIST_DELETE",
              "PLAYLIST_INSERT_ITEMS",
              "PLAYLIST_ITEMS",
              "PLAYLIST_LIST_ALL",
              
              "GET_USER_CHANNEL",
              "SEARCH",
             ]
    
