import urllib.request
import xml.etree.ElementTree as ET
import re
import os
from datetime import datetime

# 1. Configuration
# !!! MAKE SURE TO UPDATE YOUR CHANNEL ID HERE !!!
CHANNEL_ID = 'YOUR_CHANNEL_ID_HERE' 
HTML_FILE = 'NightSummary.html'
FEED_URL = f'https://youtube.com{CHANNEL_ID}'

# 2. Generate expected title using today's local date (e.g., "Death Valley Observatory Timelapse 2026-09-25")
today_str = datetime.now().strftime('%Y-%m-%d')
expected_title = f"Death Valley Observatory Timelapse {today_str}"
print(f"--- DIAGNOSTICS START ---")
print(f"Expected Video Title: '{expected_title}'")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Files found in workspace: {os.listdir('.')}")

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
                print(f"Found Matching Video ID: {video_id}")
                return video_id
                
        print(f"Warning: Could not find a video matching '{expected_title}' in the recent feed.")
    except Exception as e:
        print(f"Error reading YouTube feed: {e}")
    return None

def inject_into_html(video_id):
    if not video_id:
        print("Skipping HTML update because no matching video was found.")
        return
        
    iframe_code = f"""
    <!-- Automated YouTube Square Video Insertion -->
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <iframe width="500" height="500" 
            src="https://youtube.com{video_id}" 
            title="{expected_title}" 
            frameborder="0" 
            style="max-width: 100%; aspect-ratio: 1 / 1;"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
        </iframe>
    </div>
    """

    if not os.path.exists(HTML_FILE):
        print(f"CRITICAL ERROR: The file '{HTML_FILE}' does not exist in this directory layout!")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        content = file.read()

    print(f"HTML File Size: {len(content)} characters")

    # Match rules
    timeline_pattern = r'(<[^>]+>[^<]*Session Timeline[^<]*</[^>]+>)'
    raw_text_pattern = r'(Session Timeline)'

    if re.search(timeline_pattern, content, re.IGNORECASE):
        updated_content = re.sub(timeline_pattern, f"{iframe_code}\n\\1", content, count=1, flags=re.IGNORECASE)
        print("Success: Injected video directly above the 'Session Timeline' HTML element.")
    elif re.search(raw_text_pattern, content, re.IGNORECASE):
        updated_content = re.sub(raw_text_pattern, f"{iframe_code}\n\\1", content, count=1, flags=re.IGNORECASE)
        print("Success: Injected video directly above the raw 'Session Timeline' text string.")
    else:
        # Ultimate fail-safe if neither exists: Appends it cleanly to the end of the file string
        print("Warning: Target text or tags missing from file. Appending video to the absolute end of the file data.")
        updated_content = content + f"\n{iframe_code}"

    with open(HTML_FILE, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    print("File write operation complete.")

if __name__ == '__main__':
    target_video_id = find_video_id_by_title()
    inject_into_html(target_video_id)
    print(f"--- DIAGNOSTICS END ---")
