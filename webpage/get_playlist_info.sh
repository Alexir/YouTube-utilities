# scrape video info from youtubeclogger  playlist
# [20251116] (air
#

# https://www.youtube.com/watch?v=JUPm50llPn4&list=PLWbKjPrSYxf6Fqf0HJXPf9c_d97Z2_kZ4
# owner: (alex): https://www.youtube.com/channel/UCH2OjrqD3BorlKcR1a3HsRA

PLAYLIST="fphcUz3lw5Y&list=PLWbKjPrSYxf6Fqf0HJXPf9c_d97Z2_kZ4"
OUT_FILE="playlist_info.txt"
if [[ -f "$OUT_FILE" ]] ; then rm "$OUT_FILE" ; fi
echo -n "working..."
yt-dlp -q --skip-download \
       --print-to-file \
       "%(playlist_index)05d|%(uploader_id)s|%(upload_date,release_date)s|%(id)s|%(duration>%H:%M:%S)s|%(view_count)s|%(comment_count)s|%(title)s|%(description)s" \
       "$OUT_FILE" --replace-in-metadata title "[\|]+" "-"\
       "https://www.youtube.com/watch?v=$PLAYLIST"
echo "done"

#
