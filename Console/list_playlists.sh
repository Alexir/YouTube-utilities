#!/bin/bash 
#

# [20250104] [air] list contents of all playlists, into files by Id.
#set -x


# get list of the playlistId's for the account
mapfile -t p_lists < <( conda run -n CCC python test_youtube_api.py --tasks "PLAYLIST_LIST_ALL" )
echo "${p_lists[@]}"
# for each playlist, get all videos and write into file
for p_list in  "${p_lists[@]}"
do
    # echo "len: " ${#p_list}
    if [[ ${#p_list} -lt 1 ]] ; then continue ; fi  # ignore blank lines
    # get list of videos in playlist
    p_Id=$(awk '{print $1}' <<< $p_list)
    mapfile -t items < <( conda run -n CCC python  test_youtube_api.py --playlist $p_Id --tasks "PLAYLIST_LIST_ITEMS" )
    echo "--------------------------" $p_Id 
    if [[ -e  "playlist".$p_Id ]]; then rm "playlist".$p_Id;  fi
    echo '# '$p_list >  "playlist.$p_Id"
    
    # write per-playlist file (Id, title)
    vids=$( printf "%s\n" "${items[@]}" )
    for video in "${vids[@]}"
    do
	echo '===='
	echo $video
	echo '----'
	(awk '{print $2"\t"substr($0, index($0,$3)) }'  <<< $video) >> "playlist.$p_Id"
    done
    
done


#
