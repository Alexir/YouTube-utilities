#!/usr/bin/bash
#
# [20251118] (air) generate a new index for the playlist page.
# Assumes that you have already uploaded vidoes to Youtube and put the into the CCC playlist

# generate the access scripts:

# with claude https://claude.ai/new :  webpage_script_local.txt   ==> webpage_script_local.py
# make the index page
python  webpage_script_local.py segmented_20251108


# scrape the playlist details
bash get_playlist_info.sh

# with claude https://claude.ai/new :  webpage_script_youtube.txt ==> webpage_script_youtube.py
# make the index page
python webpage_script_youtube.py


#



