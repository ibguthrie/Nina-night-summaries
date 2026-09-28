import os
import requests
from bs4 import BeautifulSoup

api_key = os.environ["YOUTUBE_API_KEY"]
channel_id = "UCw8HtgLPR8gpic_BlYpHigA"

# 1. Fetch the latest Short from the channel
search_url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "key": api_key,
    "channelId": channel_id,
    "part": "snippet",
    "order": "date",
    "type": "video",
    "videoDuration": "short",
    "maxResults": 1
}
response = requests.get(search_url, params=params)
response.raise_for_status()
data = response.json()

video_id = data["items"][0]["id"]["videoId"]
video_title = data["items"][0]["snippet"]["title"]
print(f"Latest Short: {video_title} ({video_id})")

# 2. Build the embed iframe (tagged with an id for easy identification/removal)
embed_html = f"""
<div id="yt-short-embed" style="text-align:center; margin: 20px 0;">
  <iframe width="800" height="800"
    src="https://www.youtube.com/embed/{video_id}"
    title="{video_title}"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen>
  </iframe>
</div>
"""

# 3. Load the fresh HTML file NINA just wrote
html_path = "NightSummary/NightSummary.html"
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# 4. Safety net: remove any existing embed before inserting a new one
old_embed = soup.find("div", id="yt-short-embed")
if old_embed:
    print("Found an existing embed, removing it before inserting the new one.")
    old_embed.decompose()

# 5. Find "Session Timeline"
target = soup.find(string=lambda text: text and "Session Timeline" in text)
if not target:
    raise ValueError("Could not find 'Session Timeline' in the HTML")

parent = target.find_parent()
while parent and parent.name in ["span", "a", "strong", "em", "b", "i"]:
    parent = parent.find_parent()

if not parent:
    raise ValueError("Could not find a suitable parent element for insertion")

# 6. Inject the embed
embed_soup = BeautifulSoup(embed_html, "html.parser")
parent.insert_before(embed_soup)

# 7. Write it back, in place, before git ever sees it
with open(html_path, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"Successfully injected video into {html_path}")
