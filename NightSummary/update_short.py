import urllib.request
import xml.etree.ElementTree as ET
import re

# 1. Configuration
CHANNEL_ID = 'YOUR_CHANNEL_ID_HERE' 
HTML_FILE = 'NightSummary.html'
FEED_URL = f'https://youtube.com{CHANNEL_ID}'

def get_latest_video_id():
    try:
        response = urllib.request.urlopen(FEED_URL)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        # Define namespaces used in the YouTube RSS feed
        namespaces = {
            'atom': 'http://w3.org',
            'yt': 'http://youtube.com'
        }
        
        # Grab the first entry (the most recent video or short)
        first_entry = root.find('atom:entry', namespaces)
        if first_entry is not None:
            video_id = first_entry.find('yt:videoId', namespaces).text
            return video_id
    except Exception as e:
        print(f"Error fetching YouTube feed: {e}")
    return None

def update_html(video_id):
    if not video_id:
        return
        
    # Vertical (9:16) iframe styling optimized for Shorts
    iframe_code = f"""<!-- YOUTUBE_SHORT_START -->
<div style="display: flex; justify-content: center; margin: 20px 0;">
    <iframe width="315" height="560" 
        src="https://www.youtube.com/embed/{video_id}" 
        title="Latest YouTube Short" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
</div>
<!-- YOUTUBE_SHORT_END -->"""

    with open(HTML_FILE, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regex pattern to replace everything between the start and end tags
    pattern = r'<!-- YOUTUBE_SHORT_START -->.*?<!-- YOUTUBE_SHORT_END -->'
    
    if re.search(pattern, content, re.DOTALL):
        updated_content = re.sub(pattern, iframe_code, content, flags=re.DOTALL)
        with open(HTML_FILE, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"Successfully embedded video ID: {video_id}")
    else:
        print("Error: Could not find the replacement comment placeholders in your HTML file.")

if __name__ == '__main__':
    latest_id = get_latest_video_id()
    update_html(latest_id)
