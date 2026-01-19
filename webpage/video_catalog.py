#!/usr/bin/env python3
import os
import sys
import cv2
import shlex
from pathlib import Path
from moviepy.editor import VideoFileClip

def get_video_duration(video_path):
    """Get video duration using moviepy"""
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {e}")
        return 0

def extract_frame(video_path, time_sec, output_path):
    """Extract a frame at specified time using opencv"""
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
        success, frame = cap.read()
        cap.release()
        
        if success:
            cv2.imwrite(output_path, frame)
            return True
        return False
    except Exception as e:
        print(f"Error extracting frame from {video_path}: {e}")
        return False

def format_duration(seconds):
    """Format duration as H:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"

def split_filename(filename):
    """Split filename at last occurrence of _00., _01., _02., or _03."""
    patterns = ['_00.', '_01.', '_02.', '_03.']
    last_pos = -1
    last_pattern = None
    
    for pattern in patterns:
        pos = filename.rfind(pattern)
        if pos > last_pos:
            last_pos = pos
            last_pattern = pattern
    
    if last_pos != -1:
        return filename[:last_pos], filename[last_pos:]
    else:
        return filename, ""

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <location>")
        sys.exit(1)
    
    location = sys.argv[1]
    
    if not os.path.isdir(location):
        print(f"Error: {location} is not a valid directory")
        sys.exit(1)
    
    # Create thumb directory
    thumb_dir = Path("thumb")
    thumb_dir.mkdir(exist_ok=True)
    
    # Open video_segments file
    segments_file = open("video_segments", "w")
    
    # Find all .mp4 files with duration > 15 seconds
    video_files = []
    for mp4_file in Path(location).glob("*.mp4"):
        duration = get_video_duration(str(mp4_file))
        if duration > 15:
            video_files.append((mp4_file, duration))
    
    # Sort by filename
    video_files.sort(key=lambda x: x[0].name)
    
    # Generate HTML
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Clogger Videos</title>
    <style>
        body {
            background-color: rgb(64, 64, 64);
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        h1 {
            color: white;
        }
        table {
            background-color: rgb(128, 128, 128);
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border: 1px solid #666;
        }
        th {
            background-color: rgb(96, 96, 96);
        }
        a {
            color: lightblue;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        img {
            max-width: 200px;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>Clogger Videos</h1>
    <table>
        <tr>
            <th>Seq</th>
            <th>Thumbnail</th>
            <th>Duration</th>
            <th>Filename</th>
        </tr>
"""
    
    # Process each video
    for seq, (video_path, duration) in enumerate(video_files, start=1):
        filename = video_path.name
        thumb_name = f"thumb_{seq:02d}.jpg"
        thumb_path = thumb_dir / thumb_name
        
        # Extract frame at 30 seconds
        extract_frame(str(video_path), 30, str(thumb_path))
        
        # Format duration
        duration_str = format_duration(duration)
        
        # Apply shlex.quote to filename
        qlink = shlex.quote(str(video_path))
        
        # Split filename
        part_a, part_b = split_filename(filename)
        
        # Write to video_segments file
        segments_file.write(f"\t\t{part_a}\t{part_b}\n")
        
        # Add table row with target="_blank" for new tab
        html_content += f"""        <tr>
            <td>{seq:02d}</td>
            <td><img src="{thumb_path}" alt="Thumbnail"></td>
            <td>{duration_str}</td>
            <td><a href="{qlink}" target="_blank">{part_a}</a><br>{part_b}</td>
        </tr>
"""
    
    html_content += """    </table>
</body>
</html>
"""
    
    # Close video_segments file
    segments_file.close()
    
    # Write HTML file
    with open("index.html", "w") as f:
        f.write(html_content)
    
    print(f"Generated index.html with {len(video_files)} videos")
    print(f"Created video_segments file")

if __name__ == "__main__":
    main()
