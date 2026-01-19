#!/usr/bin/env python3
import os
import sys
import cv2
import shlex
from pathlib import Path
from moviepy.editor import VideoFileClip

def get_video_duration(video_path):
    """Get video duration in seconds using moviepy."""
    try:
        with VideoFileClip(str(video_path)) as clip:
            return clip.duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {e}")
        return 0

def extract_frame(video_path, time_seconds, output_path):
    """Extract a frame at specified time using OpenCV."""
    try:
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(time_seconds * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite(str(output_path), frame)
            return True
        return False
    except Exception as e:
        print(f"Error extracting frame from {video_path}: {e}")
        return False

def format_duration(seconds):
    """Format duration as H:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"

def split_filename(filename):
    """Split filename at the last occurrence of _00., _01., _02., or _03."""
    patterns = ['_00.', '_01.', '_02.', '_03.']
    last_pos = -1
    
    for pattern in patterns:
        pos = filename.rfind(pattern)
        if pos > last_pos:
            last_pos = pos
    
    if last_pos != -1:
        return filename[:last_pos], filename[last_pos:]
    else:
        return filename, ''

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <location>")
        sys.exit(1)
    
    location = Path(sys.argv[1])
    
    if not location.exists() or not location.is_dir():
        print(f"Error: {location} is not a valid directory")
        sys.exit(1)
    
    # Create thumb and content directories
    thumb_dir = Path('thumb')
    content_dir = Path('content')
    thumb_dir.mkdir(exist_ok=True)
    content_dir.mkdir(exist_ok=True)
    
    # Find all MP4 files with duration > 15 seconds
    video_data = []
    mp4_files = sorted(location.glob('*.mp4'))
    
    for mp4_file in mp4_files:
        duration = get_video_duration(mp4_file)
        if duration > 15:
            video_data.append({
                'path': mp4_file,
                'duration': duration,
                'filename': mp4_file.name
            })
    
    # Generate HTML
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Clogger Videos</title>
    <style>
        body {
            background-color: rgb(64, 64, 64);
            color: white;
            font-family: Arial, sans-serif;
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
            border: 1px solid white;
            color: white;
        }
        th {
            background-color: rgb(100, 100, 100);
        }
        a {
            color: white;
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
'''
    
    # Process each video
    for idx, video in enumerate(video_data, start=1):
        # Extract thumbnail at 30 seconds
        thumb_filename = f"thumb_{idx:02d}.jpg"
        thumb_path = thumb_dir / thumb_filename
        extract_frame(video['path'], 30, thumb_path)
        
        # Format duration
        duration_str = format_duration(video['duration'])
        
        # Apply shlex.quote to filename
        qlink = shlex.quote(str(video['path']))
        
        # Split filename
        part1, part2 = split_filename(video['filename'])
        
        # Add table row
        html_content += f'''        <tr>
            <td>{idx:02d}</td>
            <td><img src="../thumb/{thumb_filename}" alt="Thumbnail"></td>
            <td>{duration_str}</td>
            <td><a href="{qlink}" target="_blank">{part1}</a><br>{part2}</td>
        </tr>
'''
    
    html_content += '''    </table>
</body>
</html>
'''
    
    # Write HTML file
    output_file = content_dir / 'index.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Generated {output_file} with {len(video_data)} videos")

if __name__ == "__main__":
    main()
