from flask import Flask, request, jsonify
import requests
import re
import json

app = Flask(__name__)

def get_yt_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        # YouTube page load karna
        res = requests.get(url, headers=headers, timeout=15)
        html = res.text

        # YouTube ka hidden JSON data nikalna
        json_str = re.search(r'var ytInitialData = (\{.*?\});', html)
        if not json_str:
            return None
        
        data = json.loads(json_str.group(1))

        # Data paths (Robust extraction)
        # Title
        try:
            title = re.search(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', html).group(1)
        except:
            title = "N/A"

        # Views
        try:
            views = re.search(r'"viewCount":\{"videoViewCountRenderer":\{"viewCount":\{"simpleText":"(.*?)"\}', html).group(1)
        except:
            views = "N/A"

        # Likes
        try:
            likes = re.search(r'"defaultText":\{"simpleText":"(.*?)"\},"accessibilityText":"(.*?)"\}\},"style":"STYLE_DEFAULT"', html).group(1)
        except:
            likes = "N/A"

        # Description
        try:
            description = re.search(r'"description":\{"runs":\[\{"text":"(.*?)"\}\]', html).group(1)
        except:
            description = "N/A"

        return {
            "title": title,
            "views": views,
            "likes": likes,
            "description": description.replace('\\n', '\n')[:500] + "...", # Pehle 500 characters
            "dev_by": "@Configexe"
        }
    except Exception:
        return None

@app.route('/yt-extract')
def main():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"status": "error", "message": "URL missing"}), 400

    info = get_yt_info(video_url)
    
    if info:
        return jsonify({
            "status": "success",
            "project": "teamexe-yt-video-info",
            "data": info
        })
    else:
        return jsonify({"status": "error", "message": "Failed to extract. Try again."}), 500

@app.route('/')
def home():
    return "<h1>TeamExe API is 100% Online</h1>"

# For Vercel
app = app
    
