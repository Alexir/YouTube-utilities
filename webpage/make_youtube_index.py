import sys
import pandas as pd
from pathlib import Path
import re

def split_title(title):
    """Split title at first occurrence of ' 00 ', ' 01 ', ' 02 ', or ' 03 '"""
    patterns = [' 00 ', ' 01 ', ' 02 ', ' 03 ']
    
    for pattern in patterns:
        if pattern in title:
            parts = title.split(pattern, 1)
            return parts[0], pattern + parts[1]
    
    return title, ""

def generate_html(mp4files):
    """Generate HTML page with video information"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Clogger Videos</title>
    <style>
        body {
            background-color: #404040;
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        h1 {
            color: white;
            text-align: center;
        }
        table {
            background-color: #808080;
            border-collapse: collapse;
            width: 100%;
            margin: 20px auto;
        }
        th, td {
            padding: 10px;
            border: 1px solid #666;
            color: white;
        }
        th {
            background-color: #666;
        }
        .fixed-width {
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        a {
            color: white;
        }
        img {
            display: block;
        }
    </style>
</head>
<body>
    <h1>Clogger Videos</h1>
    <table>
        <thead>
            <tr>
                <th>Seq</th>
                <th>Thumbnail</th>
                <th>Duration</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for _, row in mp4files.iterrows():
        seq = row.iloc[0]  # Field 1
        youtube_id = row.iloc[3]  # Field 4
        duration = row.iloc[4]  # Field 5
        views = row.iloc[5]  # Field 6
        likes = row.iloc[6]  # Field 7
        title = row.iloc[7]  # Field 8
        description = row.iloc[8]  # Field 9
        
        # Generate thumbnail URL and video link
        thumbnail_url = f"https://img.youtube.com/vi/{youtube_id}/mqdefault.jpg"
        video_url = f"https://www.youtube.com/watch?v={youtube_id}"
        
        # Split title
        title_part1, title_part2 = split_title(title)
        
        # Build the details column HTML
        details_html = f"{title_part1}"
        if title_part2:
            details_html += f"<br><span class='fixed-width'>{title_part2}</span>"
        details_html += f"<br><br>DESCRIPTION: {description}"
        details_html += f"<br><br>VIEWS: {views}"
        details_html += f"<br>LIKES: {likes}"
        
        # Add row to table
        html += f"""            <tr>
                <td>{seq}</td>
                <td><a href="{video_url}" target="_blank"><img src="{thumbnail_url}" alt="Video thumbnail"></a></td>
                <td>{duration}</td>
                <td>{details_html}</td>
            </tr>
"""
    
    html += """        </tbody>
    </table>
</body>
</html>"""
    
    return html

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Read CSV with pipe delimiter
    mp4files = pd.read_csv(csv_file, delimiter='|', header=None)
    
    # Print number of rows
    print(f"Number of rows in mp4files: {len(mp4files)}")
    
    # Generate HTML
    html_content = generate_html(mp4files)
    
    # Write to file
    output_file = Path('videos_youtube.html')
    output_file.write_text(html_content, encoding='utf-8')
    
    print(f"HTML file created: {output_file}")

if __name__ == "__main__":
    main()
