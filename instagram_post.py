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
                           "Your goal is to analyze the given content, extract the key visual elements, and generate a professional, structured image prompt. "
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
    draw.rectangle(
        [(text_x - 20, text_y - 20), (text_x + text_width + 20, text_y + 80)],
        fill="black"
    )
    draw.text((text_x, text_y), headline, font=font, fill="white")

    # 🔹 Convert Image to Video
    image_bytes = io.BytesIO()
    background.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    imaget = Image.open(image_bytes).convert("RGB")
    image_np = np.array(imaget)
    video_clip = ImageSequenceClip([image_np] * 15, fps=1)
    temp_video_path = "temp_video.mp4"
    video_clip.write_videofile(temp_video_path, codec="libx264", fps=24, logger=None)

    # 🔹 4. Merge Video with Music
    music_path = "/ReelAudio.mp3"  
    temp_merged_video_path = "temp_merged_video.mp4"

    ffmpeg_command = [
        "ffmpeg",
        "-i", temp_video_path,
        "-i", music_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        "-shortest",
        temp_merged_video_path
    ]
    subprocess.run(ffmpeg_command, check=True)

    # 🔹 5. Upload Video to Cloudinary
    cloudinary.config(
        cloud_name="dkr5qwdjd",
        api_key="797349366477678",
        api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"
    )
    upload_result = cloudinary.uploader.upload_large(
        temp_merged_video_path,
        resource_type="video",
        chunk_size=6000000,
        folder="generated_images"
    )

    os.remove(temp_video_path)
    os.remove(temp_merged_video_path)

    final_url = upload_result["secure_url"]
    print("✅ Final Instagram Reel URL:", final_url)

    # 🔹 6. Upload & Publish the Instagram Reel
    upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "video_url": final_url,
        "caption": caption_text,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(upload_url, data=payload)
    response_data = response.json()
    print(response_data)

    media_id = response_data.get("id")

    if media_id:
        print("⏳ Waiting for Instagram to process the video...")
        time.sleep(10)  

        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        print("✅ Reel Uploaded Successfully!", publish_response.json())
    else:
        print("❌ Error: Failed to upload the video.")

# 🔹 Schedule it to run daily at 7 PM IST (14:00 UTC)
schedule.every().day.at("15:46").do(post_reel)

# 🔹 Start Scheduler in a Background Thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# 🔹 Run Flask on Render (Port 10000)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
