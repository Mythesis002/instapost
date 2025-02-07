import requests
import re
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont
import cloudinary
import cloudinary.uploader
import io
from moviepy.editor import ImageSequenceClip
import numpy as np
import subprocess
import textwrap
import os
import time
import schedule
import datetime
import threading
from flask import Flask

# 🔹 Flask Web Server for Render
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Instagram Reel Bot is Running!"

# 🔹 Instagram Credentials
ACCESS_TOKEN = "EAAWYAavlRa4BO8OE7Ho6gtx4a85DRgNMc59ZCpAdsHXNJnbZABREkXovZCKnbo9AlupOjbJ5xYSTBrMIMTVtu9n530I3ZC2JZBuZBpCDzHyjI7ngh8EtCrSvUho9VGZB9Xdxt5JLGNrHwfDsSIqtvxFjefG2t2JsgJpqfZAMCjO8AURp79mU0WAaLA7R"
INSTAGRAM_ACCOUNT_ID = "17841468918737662"
INSTAGRAM_NICHE_ACCOUNT = "evolving.ai"

# ✅ Ensure `ReelAudio.mp3` is present
AUDIO_FILE = os.path.join(os.getcwd(), "ReelAudio.mp3")
if not os.path.exists(AUDIO_FILE):
    raise FileNotFoundError(f"❌ Audio file missing: {AUDIO_FILE}")

def post_reel():
    """Uploads and posts an Instagram Reel automatically."""
    print(f"📅 Running at: {datetime.datetime.now()}")

    # 🔹 1. Get Instagram Caption
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/posts"
    querystring = {"username_or_id_or_url": INSTAGRAM_NICHE_ACCOUNT}
    headers = {
        "x-rapidapi-key": "628e474f5amsh0457d8f1b4fb50cp16b75cjsn70408f276e9b",
        "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code != 200:
        print(f"❌ Error fetching Instagram caption: {response.text}")
        return
    data = response.json()
    caption_text = data['data']['items'][0]['caption']['text']

    # 🔹 2. Generate Headline & Image Prompt
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that specializes in converting text descriptions into high-quality, "
                           "crunchy Instagram headlines for text overlays and detailed image prompts for AI image generation. "
                           "Your goal is to analyze the given content, extract key visual elements, and generate a professional, structured image prompt. "
                           "Additionally, generate a short, crunchy hooking headline (maximum 5 words) that summarizes the image concept."
            },
            {
                "role": "user",
                "content": caption_text
            }
        ],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "628e474f5amsh0457d8f1b4fb50cp16b75cjsn70408f276e9b",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    # 🔹 Extract Headline & Image Prompt
    result_text = response_data.get("result", "")
    headline_match = re.search(r'\*\*Headline:\*\*\n"(.+?)"', result_text)
    headline = headline_match.group(1) if headline_match else "No headline found"
    image_prompt_match = re.search(r'\*\*Image Prompt:\*\*\n(.+)', result_text, re.DOTALL)
    image_prompt = image_prompt_match.group(1).strip() if image_prompt_match else "No image prompt found"

    # 🔹 3. Generate Image & Create Video
    client = InferenceClient(token="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")
    model = "black-forest-labs/FLUX.1-dev"
    image_data = client.text_to_image(image_prompt, model=model)

    # 🔹 Resize & Apply Background
    image = image_data.resize((900, 900))
    background = Image.new("RGB", (1080, 1920), (0, 0, 0))
    background.paste(image, (90, 510))

    # 🔹 Add Headline to Image
    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    text_width = draw.textlength(headline, font=font)
    text_x = (1080 - text_width) // 2
    text_y = 320
    draw.text((text_x, text_y), headline, font=font, fill="white")

    # 🔹 Convert Image to Video
    temp_video_path = "temp_video.mp4"
    video_clip = ImageSequenceClip([np.array(background)] * 15, fps=1)
    video_clip.write_videofile(temp_video_path, codec="libx264", fps=24)

    # 🔹 4. Merge Video with Music
    temp_merged_video_path = "temp_merged_video.mp4"
    ffmpeg_command = [
        "ffmpeg",
        "-i", temp_video_path,
        "-i", AUDIO_FILE,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        "-shortest",
        temp_merged_video_path
    ]
    subprocess.run(ffmpeg_command, check=True)

    # 🔹 5. Upload Video to Instagram
    upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "video_url": temp_merged_video_path,
        "caption": caption_text,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(upload_url, data=payload)
    if response.status_code != 200:
        print(f"❌ Upload Failed: {response.text}")
        return
    print("✅ Reel Uploaded Successfully!")

# 🔹 Schedule it to run daily at 8:46 PM IST
schedule.every().day.at("05:40").do(post_reel)  

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

# 🔹 Start Flask in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# 🔹 Run Flask Web Server on Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
