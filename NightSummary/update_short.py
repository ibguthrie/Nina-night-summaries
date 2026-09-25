import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# 1. Configuration
# !!! MAKE SURE TO UPDATE YOUR CHANNEL ID HERE !!!
CHANNEL_ID = '@bguthrie' 
HTML_FILE = 'NightSummary.html'
FEED_URL = f'https://youtube.com{CHANNEL_ID}'

# 2. Generate expected title using today's date (e.g., "Death Valley Observatory Timelapse 2026-09-25")
today_str = datetime.now().strftime('%Y-%m-%d')
expected_title = f"Death Valley Observatory Timelapse {today_str}"
print(f"Searching YouTube feed for: '{expected_title}'")

def find_video_id_by_title():
    try:
        response = urllib.request.urlopen(FEED_URL)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        namespaces = {
            'atom': 'http://w3.org',
            'yt': 'http://youtube.com'
        }
        
        for entry in root.findall('atom:entry', namespaces):
            title = entry.find('atom:title', namespaces).text
            if expected_title.lower() in title.lower():
                video_id = entry.find('yt:videoId', namespaces).text
                return video_id
                
        print(f"Warning: Could not find a video matching '{expected_title}' in the recent feed.")
    except Exception as e:
        print(f"Error reading YouTube feed: {e}")
    return None

def inject_into_html(video_id):
    if not video_id:
        print("Skipping HTML update because no matching video was found.")
        return
        
    # Standard responsive video embed layout
    iframe_code = f"""
    <!-- Automated YouTube Short Insertion -->
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <iframe width="315" height="560" 
            src="https://youtube.com{video_id}" 
            title="{expected_title}" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
        </iframe>
    </div>
    """

    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        content = file.read()

    # Strategy: Find the opening <body> tag and place the video right after it
    body_pattern = r'(<body[^>]*>)'
    
    if re.search(body_pattern, content, re.IGNORECASE):
        # Insert the iframe code immediately after the <body> tag opens
        updated_content = re.sub(body_pattern, f"\\1\n{iframe_code}", content, count=1, flags=re.IGNORECASE)
        
        with open(HTML_FILE, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"Successfully injected Short (ID: {video_id}) into the fresh HTML file.")
    else:
        print("Error: Could not find a <body> tag in the generated HTML file.")

if __name__ == '__main__':
    target_video_id = find_video_id_by_title()
    inject_into_html(target_video_id)
