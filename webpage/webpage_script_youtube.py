#!/usr/bin/env python3
import sys
import csv
import cv2
from pathlib import Path
from moviepy.editor import VideoFileClip
import yt_dlp

def split_title(title):
    """Split title at the first occurrence of ' 00 ', ' 01 ', ' 02 ', or ' 03 '."""
    patterns = [' 00 ', ' 01 ', ' 02 ', ' 03 ']
    first_pos = len(title)
    found_pattern = None
    
    for pattern in patterns:
        pos = title.find(pattern)
        if pos != -1 and pos < first_pos:
            first_pos = pos
            found_pattern = pattern
    
    if found_pattern:
        return title[:first_pos], title[first_pos:]
    else:
        return title, ''

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file>")
        sys.exit(1)
    
    csv_file = Path(sys.argv[1])
    
    if not csv_file.exists():
        print(f"Error: {csv_file} does not exist")
        sys.exit(1)
    
    # Read CSV file with | delimiter
    mp4files = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        for row in reader:
            mp4files.append(row)
    
    print(f"Number of rows: {len(mp4files)}")
    
    # Read legend.txt
    legend_text = ""
    legend_file = Path('legend.txt')
    if legend_file.exists():
        with open(legend_file, 'r', encoding='utf-8') as f:
            legend_text = f.read()
    
    # Generate HTML
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Clogger Videos</title>
    <style>
        body {
            background-color: rgb(31, 31, 31);
            color: white;
            font-family: Arial, sans-serif;
        }
        h1 {
            color: white;
        }
        p {
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
            vertical-align: top;
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
        .title-part1 {
            font-weight: bold;
        }
        .title-part2 {
            font-family: monospace;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>Clogger Videos</h1>
'''
    
    # Add legend paragraph
    if legend_text:
        html_content += f'    <p>{legend_text}</p>\n'
    
    html_content += '''    <table>
        <tr>
            <th>Seq</th>
            <th>Thumbnail</th>
            <th>Duration</th>
            <th>Details</th>
        </tr>
'''
    
    # Process each row
    for row in mp4files:
        if len(row) < 9:
            continue
        
        seq = row[0] if len(row) > 0 else ''
        youtube_id = row[3] if len(row) > 3 else ''
        duration = row[4] if len(row) > 4 else ''
        views = row[5] if len(row) > 5 else ''
        likes = row[6] if len(row) > 6 else ''
        title = row[7] if len(row) > 7 else ''
        description = row[8] if len(row) > 8 else ''
        
        # Generate YouTube thumbnail URL
        thumb_url = f"https://img.youtube.com/vi/{youtube_id}/mqdefault.jpg"
        video_url = f"https://www.youtube.com/watch?v={youtube_id}"
        
        # Split title
        title_part1, title_part2 = split_title(title)
        
        # Build details cell content
        details = f'<span class="title-part1">{title_part1}</span>'
        if title_part2:
            details += f'<br><span class="title-part2">{title_part2}</span>'
        details += '<br><br>'
        details += f'DESCRIPTION: {description}<br>'
        details += f'VIEWS: {views} LIKES: {likes}'
        
        # Add table row
        html_content += f'''        <tr>
            <td>{seq}</td>
            <td><a href="{video_url}" target="_blank"><img src="{thumb_url}" alt="Thumbnail"></a></td>
            <td style="vertical-align: top;">{duration}</td>
            <td>{details}</td>
        </tr>
'''
    
    html_content += '''    </table>
</body>
</html>
'''
    
    # Write HTML file
    output_file = Path('videos_youtube.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated {output_file} with {len(mp4files)} videos")

if __name__ == "__main__":
    main()
