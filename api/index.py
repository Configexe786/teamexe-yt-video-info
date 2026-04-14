from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def capture_from_toolsoverflow(yt_url):
    target_site = "https://www.toolsoverflow.com/youtube/youtube-title-description-extractor"
    
    # ToolOverflow ko request bhejna
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Referer": target_site
    }
    
    try:
        # Step 1: ToolOverflow ke backend ko simulate karna
        # Note: Ye site aksar POST request leti hai data dikhane ke liye
        session = requests.Session()
        res = session.post(target_site, data={"url": yt_url}, headers=headers, timeout=20)
        
        if res.status_code != 200:
            # Agar POST fail ho toh GET try karte hain (kuch sites URL params leti hain)
            res = session.get(f"{target_site}?url={yt_url}", headers=headers, timeout=20)

        soup = BeautifulSoup(res.text, 'html.parser')

        # Step 2: Elements capture karna (Based on your screenshots)
        # Hum generic selectors use karenge jo text content se match karein
        data = {
            "title": "Not Found",
            "description": "Not Found",
            "views": "0",
            "likes": "0",
            "comments": "0"
        }

        # Title aur Description capture
        textareas = soup.find_all('textarea')
        if len(textareas) >= 1: data["title"] = textareas[0].get_text(strip=True)
        if len(textareas) >= 2: data["description"] = textareas[1].get_text(strip=True)

        # Views, Likes, Comments capture (Looking for icons or specific text)
        stats = soup.find_all(['div', 'span', 'p'], class_=lambda x: x and ('stats' in x or 'count' in x or 'flex' in x))
        for item in stats:
            text = item.get_text(strip=True)
            if 'K' in text or 'M' in text or text.isdigit():
                if not data["views"] or data["views"] == "0": data["views"] = text
                elif not data["likes"] or data["likes"] == "0": data["likes"] = text
                elif not data["comments"] or data["comments"] == "0": data["comments"] = text

        return data
    except Exception as e:
        return {"error": str(e)}

@app.route('/yt-extract')
def extract():
    url = request.args.get('url')
    if not url:
        return jsonify({"status": "error", "message": "YouTube URL missing"}), 400
    
    # ToolOverflow se data capture karna
    captured_data = capture_from_toolsoverflow(url)
    
    return jsonify({
        "status": "success",
        "website_source": "toolsoverflow.com",
        "data": captured_data,
        "dev": "@Configexe"
    })

@app.route('/')
def home():
    return "<h1>TeamExe ToolOverflow Scraper is Live!</h1>"

app = app
            
