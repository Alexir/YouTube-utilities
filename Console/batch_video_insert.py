#!python
#

# [20260114] (air) insert a list of videos, with meta info
# data taken from .ods file with notes; notes go into description
#

import sys, os

import time
from datetime import datetime,timedelta
import isodate
import random
import json
import argparse
import csv
from io import StringIO

from pyexcel_odsr import get_data
import googleapiclient.discovery
import googleapiclient.errors
from apiclient.http import MediaFileUpload

from youtube_core import *

parser = argparse.ArgumentParser()
parser.add_argument("--infile", help="ods file to process", required=True)
parser.add_argument("--outfile", help="output file", required=True)
parser.add_argument("--media", help="the video to insert", required=False)
parser.add_argument("--folder", help="data folder, for in and out)", default=".")
args = parser.parse_args()

media_file = args.media
part = 'snippet, status'

client = get_youtube()   ## get a connection
    

data = get_data(args.infile)
# print( json.dumps(data,indent=4))

for row in data["Sheet1"] :
    if len(row) == 1 : continue  # not a video file
    
    if len(row) < 6 :  row = row + [""]   #  .ods file won't have an empty note field
    (file,fsize,duration,aspect,quality,note) = row
    title = 'title goes here'
    description = title+"\n"+\
        str(fsize)+'\n'+\
        duration+'\n'\
        +aspect+'\n'+\
        quality+'\n'+\
        note+'\n' # fix fsize->str

    description = f"file: {file}\nlength: {duration}\naspect: {aspect}\nquality: {quality}\nnote: {note}"
    media_file= os.path.join(args.folder,title)

    properties = {
        'snippet.title': title,
        'snippet.description': description,
        'snippet.tags': [ '#coalcountrycloggers', '#cloggers' ],
        
        'status.selfDeclaredMadeForKids': "False",
        'snippet.categoryId': '27',  # "education"
        'snippet.defaultLanguage': 'EN',  # assumed...
        'status.embeddable': '',
        'status.license': '',  # CC?
        'status.privacyStatus': 'private',  # remember to change when ready
        'status.publicStatsViewable': '',
    }
    
    media_obj = MediaFileUpload(media_file, chunksize =-1, resumable = True)
    resource = build_resource(properties)
    request = client.videos().insert(
        body = resource,
        media_body = media_obj,
        part='snippet, status',
        )
    print("\n")
    print( request )

    response = resumable_upload( request, 'video', 'insert' )  ## upload
    print(response)

#

