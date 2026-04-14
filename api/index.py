from flask import Flask, request, jsonify
import requests
import re
import json

app = Flask(__name__)

def scrape_youtube(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        # Direct YouTube page se data capture karna
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        # Metadata capture logic
        json_data = re.search(r'var ytInitialData = (\{.*?\});', html)
        if not json_data:
            return None
            
        data = json.loads(json_data.group(1))
        
        # Data paths extraction
        contents = data['contents']['twoColumnWatchNextResults']['results']['results']['contents']
        primary = contents[0]['videoPrimaryInfoRenderer']
        secondary = contents[1]['videoSecondaryInfoRenderer']

        # 1. Title capture
        title = primary['title']['runs'][0]['text']
        
        # 2. Views capture
        views = primary['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
        
        # 3. Likes capture
        likes = "N/A"
        try:
            buttons = primary['videoActions']['menuRenderer']['topLevelButtons']
            for b in buttons:
                if 'segmentedLikeDislikeButtonRenderer' in b:
                    likes = b['segmentedLikeDislikeButtonRenderer']['likeButton']['toggleButtonRenderer']['defaultText']['simpleText']
        except: pass

        # 4. Description capture
        description = ""
        try:
            description = secondary['description']['runs'][0]['text']
        except: pass

        return {
            "title": title,
            "views": views,
            "likes": likes,
            "description": description,
            "status": "Success"
        }
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.route('/yt-extract')
def extract():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
        
    data = scrape_youtube(video_url)
    if data and data['status'] == "Success":
        return jsonify(data)
    return jsonify({"error": "Failed to scrape data"}), 500

@app.route('/')
def home():
    return "<h1>TeamExe YT API is Online!</h1><p>Use /yt-extract?url=LINK</p>"

app = app
            
