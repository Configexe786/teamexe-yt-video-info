from flask import Flask, request, jsonify
import requests
import re
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_yt_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # YouTube ka internal data dhundna (Title, Views, Description ke liye)
    # Ye wahi capture logic hai jo screenshots me dikh raha hai
    data_re = re.compile(r'var ytInitialData = (\{.*?\});')
    match = data_re.search(response.text)
    
    if not match:
        return None
    
    yt_data = json.loads(match.group(1))
    
    # Metadata extraction
    try:
        video_details = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
        video_secondary = yt_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']
        
        title = video_details['title']['runs'][0]['text']
        # Views count extraction
        views = video_details['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
        # Likes count
        likes = video_details.get('videoActions', {}).get('menuRenderer', {}).get('topLevelButtons', [{}])[0].get('segmentedLikeDislikeButtonRenderer', {}).get('likeButton', {}).get('toggleButtonRenderer', {}).get('defaultText', {}).get('simpleText', 'N/A')
        # Description extraction
        description = video_secondary['description']['runs'][0]['text'] if 'runs' in video_secondary['description'] else ""

        return {
            "title": title,
            "views": views,
            "likes": likes,
            "comments": "Available via YouTube API", # Comments scraping requires heavy JS
            "description": description
        }
    except:
        return None

@app.route('/yt-info', methods=['GET'])
def get_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"status": "error", "message": "Please provide a YouTube URL"}), 400

    data = extract_yt_data(video_url)
    
    if data:
        return jsonify({
            "status": "success",
            "capture_details": data,
            "source": "Direct YouTube Capture",
            "credits": "@Configexe"
        })
    else:
        return jsonify({"status": "error", "message": "Failed to capture data from YouTube"}), 500

@app.route('/')
def home():
    return "<h1>YT Extractor API is Online!</h1><p>Use /yt-info?url=YOUR_URL</p>"

app = app
  
