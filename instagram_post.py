import requests
import re
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
import numpy as np
import os
import time
import schedule
import datetime

# 🔹 Instagram Credentials
ACCESS_TOKEN = "EAAWYAavlRa4BO8OE7Ho6gtx4a85DRgNMc59ZCpAdsHXNJnbZABREkXovZCKnbo9AlupOjbJ5xYSTBrMIMTVtu9n530I3ZC2JZBuZBpCDzHyjI7ngh8EtCrSvUho9VGZB9Xdxt5JLGNrHwfDsSIqtvxFjefG2t2JsgJpqfZAMCjO8AURp79mU0WAaLA7R"
INSTAGRAM_ACCOUNT_ID = "17841468918737662"
INSTAGRAM_NICHE_ACCOUNT = "techinlast24hr"

def post_reel():
    """Uploads and posts an Instagram Reel automatically."""
    print(f"📅 Running at: {datetime.datetime.now()}")

    # 🔹 1. Get Instagram Caption
    url = "https://instagram230.p.rapidapi.com/user/posts"
    querystring = {"username": INSTAGRAM_NICHE_ACCOUNT}
    headers = {
        "x-rapidapi-key": "c66b66fd5fmsh2d1f2d4c5d0a073p17161ajsnb75f8dbbac1d",
        "x-rapidapi-host": "instagram230.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        # Check if 'items' is in data and it's not empty before accessing its elements
        if 'items' in data and data['items'] and isinstance(data['items'], list) and len(data['items']) > 0:
            # Access the caption text from the first item in the 'items' list
            caption_text = data['items'][0]['caption']['text']

            # Check if 'music_metadata' and 'music_canonical_id' exist
            if 'music_metadata' in data['items'][0] and data['items'][0]['music_metadata'] and 'music_canonical_id' in data['items'][0]['music_metadata']:
                music_canonical_id = data['items'][0]['music_metadata']['music_canonical_id']
            else:
                # Use the default ID if 'music_canonical_id' is missing or invalid
                music_canonical_id = "18149596924049565"

                print("Music Canonical ID:", music_canonical_id)
        else:
            # Handle the case where the expected structure is not found
            print("Error: Unexpected response structure or empty 'items' list.")
            print(data)  # Print the response for debugging
            return
        url = "https://instagram-scraper-api2.p.rapidapi.com/v1/audio_info"

        querystring = {"audio_canonical_id":music_canonical_id}

        headers = {
         	"x-rapidapi-key": "c4149d7f42msh169b1ac1d7c079ep17cebfjsn882b5a92dacd",
	        "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        print(response.json())
        music_url = data['data']['download_url']
        print(music_url)
        cloudinary.config(
                cloud_name="dkr5qwdjd",
                api_key="797349366477678",
                api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"
            )
        upload_result = cloudinary.uploader.upload(music_url, resource_type="video")

    # 🔹 Print Public ID
        music_public_id = upload_result.get("public_id")
        print(f"✅ Uploaded Successfully! Public ID: {music_public_id}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch Instagram caption: {e}")


    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    payload = {
        "messages": [
            {
                "role": "system",
                "content":
                "You are an AI assistant that specializes in generating high-quality Instagram post elements. "
                "For any given caption, you must return:\n"
                "1️⃣ **Instagram Headline**: A detailed short, attention-grabbing headline (min 2lines).\n"
                "2️⃣ **Image Prompt**: A detailed description of the ideal AI-generated image.\n\n"
                "Format your response **exactly** like this:\n"
                "**Headline:** Your catchy headline here\n"
                "**Image Prompt:** Your detailed image description here"
            },
            {
                "role": "user",
                "content": caption_text
            }
        ],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "c66b66fd5fmsh2d1f2d4c5d0a073p17161ajsnb75f8dbbac1d",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    result_text = response_data.get("result", "").strip()




    headline_pattern = r'\*\*Headline:\*\*\s*(.+)'
    image_prompt_pattern = r'\*\*Image Prompt:\*\*\s*(.+)'

    headline_match = re.search(headline_pattern, result_text)
    image_prompt_match = re.search(image_prompt_pattern, result_text)

    headline = headline_match.group(1).strip() if headline_match else "No headline found"
    image_prompt = image_prompt_match.group(1).strip() if image_prompt_match else "No image prompt found"


    # 🔹 3. Generate Image & Create Video
    client = InferenceClient(token="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")
    model = "black-forest-labs/FLUX.1-dev"
    image = client.text_to_image(image_prompt, model=model)





    # 🔹 5. Upload Video to Cloudinary
    cloudinary.config(
        cloud_name="dkr5qwdjd",
        api_key="797349366477678",
        api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"
    )
    # Convert the PIL Image to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')  # Or whichever format you prefer
    image_bytes.seek(0)  # Reset the stream position


    upload_result = cloudinary.uploader.upload(image_bytes.getvalue(), folder="Mythesis_images")
    public_id = upload_result["public_id"].replace("/", ":")

    music_id = music_public_id

    video_url = cloudinary.CloudinaryVideo("bgvideo1").video(transformation=[
    # Main Image Overlay (Product/Feature Image)
      {
      'overlay': public_id,
      'width': 400,
      'height': 400,
      'crop': "pad",
      'y': 130,
      'background': "#000000", 'gravity': "north"
      },
      {'background': "#000000", 'gravity': "north", 'height': 1920, 'width': 1080, 'crop': "pad"},
      {'effect': "gradient_fade:symmetric_pad", 'x': "0.5"},
      {'effect': 'gen_restore'},
      {'effect': "fade:2000"},
      {
      'flags': "layer_apply",
      'width': 1080,
      'crop': "pad",
      'gravity': "center",
      'y': -130  # Moves image 100 pixels up
      },
      {"overlay": f"audio:{music_public_id}", "start_offset": "40", "duration": "15"},
      {'effect':"volume:1000"},
      {'flags': "layer_apply"},
      {'width': 500, 'crop': "scale"},

        # Corrected text overlay parameters
      {
      'overlay': {
      'font_family': "georgia",
      'font_size': 30,
      'gravity': "center",
      'y': -30,
      'text_align': "center",
      'text': headline
      },
      'color': "white",
      'effect': "fade:2000",
      'text_align': "center",
      'width': 450,
      'crop': "fit",
      'gravity': "center",
      'y': 100,# Align text to the center
      }
    ])

    match = re.search(r'/webm"><source src="(.*\.mp4)"', str(video_url))
    mp4_url = match.group(1)
    print(mp4_url)


    # 🔹 6. Upload & Publish the Instagram Reel
    upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "video_url": mp4_url,
        "caption": caption_text,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(upload_url, data=payload)
    response_data = response.json()
    print(response_data)

    media_id = response_data.get("id")
    print(media_id)

    if media_id:
        print("⏳ Waiting for Instagram to process the video...")
        time.sleep(140)

        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        print("✅ Reel Uploaded Successfully!", publish_response.json())
    else:
        print("❌ Error: Failed to upload the video.")

post_reel()
