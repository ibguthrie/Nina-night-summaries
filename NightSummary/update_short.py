import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# 1. Configuration
CHANNEL_ID = 'YOUR_CHANNEL_ID_HERE' 
HTML_FILE = 'NightSummary.html'
FEED_URL = f'https://youtube.com{CHANNEL_ID}'

# 2. Generate expected title (e.g., "Death Valley Observatory Timelapse 2026-09-25")
today_str = datetime.utcnow().strftime('%Y-%m-%d')
expected_title = f"Death Valley Observatory Timelapse {today_str}"
print(f"Searching for video titled: '{expected_title}'")

def find_video_id_by_title():
    try:
        response = urllib.request.urlopen(FEED_URL)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        namespaces = {
            'atom': 'http://w3.org',
            'yt': 'http://youtube.com'
        }
        
        # Loop through recent videos in the feed
        for entry in root.findall('atom:entry', namespaces):
            title = entry.find('atom:title', namespaces).text
            
            # Check if today's expected title is inside the video title
            if expected_title.lower() in title.lower():
                video_id = entry.find('yt:videoId', namespaces).text
                return video_id
                
        print(f"Warning: Could not find a video matching '{expected_title}' in the recent feed.")
    except Exception as e:
        print(f"Error reading YouTube feed: {e}")
    return None

def update_html(video_id):
    if not video_id:
        print("Skipping HTML update because no matching video was found.")
        return
        
    iframe_code = f"""<!-- YOUTUBE_SHORT_START -->
<div style="display: flex; justify-content: center; margin: 20px 0;">
    <iframe width="315" height="560" 
        src="https://youtube.com{video_id}" 
        title="{expected_title}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
</div>
<!-- YOUTUBE_SHORT_END -->"""

    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r'<!-- YOUTUBE_SHORT_START -->.*?<!-- YOUTUBE_SHORT_END -->'
    
    if re.search(pattern, content, re.DOTALL):
        updated_content = re.sub(pattern, iframe_code, content, flags=re.DOTALL)
        with open(HTML_FILE, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"Successfully embedded today's Short (ID: {video_id})")
    else:
        print("Error: Could not find the <!-- YOUTUBE_SHORT_START --> placeholders in NightSummary.html.")

if __name__ == '__main__':
    target_video_id = find_video_id_by_title()
    update_html(target_video_id)
