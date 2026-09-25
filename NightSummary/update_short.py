import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# 1. Configuration
# !!! MAKE SURE TO UPDATE YOUR CHANNEL ID HERE !!!
CHANNEL_ID = 'YOUR_CHANNEL_ID_HERE' 
HTML_FILE = 'NightSummary.html'
FEED_URL = f'https://youtube.com{CHANNEL_ID}'

# 2. Generate expected title using today's local date (e.g., "Death Valley Observatory Timelapse 2026-09-25")
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
        
    # Responsive square layout (1:1 ratio)
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

    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        content = file.read()

    # STRATEGY 1: Aggressive search for 'Session Timeline' regardless of the tag types or white spaces
    # This matches <h2>Session Timeline</h2>, <p><b>Session Timeline</b></p>, etc.
    timeline_pattern = r'(<[^>]+>[^<]*Session Timeline[^<]*</[^>]+>)'
    
    # STRATEGY 2: Absolute raw text fallback if it's completely un-tagged raw text
    raw_text_pattern = r'(Session Timeline)'

    if re.search(timeline_pattern, content, re.IGNORECASE):
        updated_content = re.sub(timeline_pattern, f"{iframe_code}\n\\1", content, count=1, flags=re.IGNORECASE)
        print("Success: Found the 'Session Timeline' HTML element! Injecting video directly above it.")
    elif re.search(raw_text_pattern, content, re.IGNORECASE):
        updated_content = re.sub(raw_text_pattern, f"{iframe_code}\n\\1", content, count=1, flags=re.IGNORECASE)
        print("Success: Found raw 'Session Timeline' text. Injecting video directly above it.")
    else:
        # STRATEGY 3: Ultimate Fallback — place at the bottom of the page if the text is completely missing
        print("Warning: Could not find 'Session Timeline' text anywhere in the document. Using </body> fallback...")
        body_close_pattern = r'(</body>)'
        if re.search(body_close_pattern, content, re.IGNORECASE):
            updated_content = re.sub(body_close_pattern, f"{iframe_code}\n\\1", content, count=1, flags=re.IGNORECASE)
            print("Success: Placed the video right before the closing body tag.")
        else:
            print("CRITICAL ERROR: Could not find any target elements or closing body tags in the file.")
            import sys
            sys.exit(2) # This is what triggered your error code exit

    # Write the changes back out safely
    with open(HTML_FILE, 'w', encoding='utf-8') as file:
        file.write(updated_content)


if __name__ == '__main__':
    target_video_id = find_video_id_by_title()
    inject_into_html(target_video_id)
