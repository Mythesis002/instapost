import requests
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import base64
import time
import random
import google.auth
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import re
import pickle

# Constantss
CLIENT_SECRETS_FILE = "client_secrets.json"  # Your OAuth JSON file
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Maximum retry attempts for failed uploads
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

ACCESS_TOKEN = "EAAWYAavlRa4BO8OE7Ho6gtx4a85DRgNMc59ZCpAdsHXNJnbZABREkXovZCKnbo9AlupOjbJ5xYSTBrMIMTVtu9n530I3ZC2JZBuZBpCDzHyjI7ngh8EtCrSvUho9VGZB9Xdxt5JLGNrHwfDsSIqtvxFjefG2t2JsgJpqfZAMCjO8AURp79mU0WAaLA7R"
INSTAGRAM_ACCOUNT_ID = "17841468918737662"

# ✅ Step 2: Generate Audio using ElevenLabs
API_VOICE_KEY = "sk_aa9b2128c2fb988e43c4969e0327572f8fe305f12c1437a3"
VOICE_ID = "m977HV2TDqAAgMuLtvWa"

url = "https://ai-deepsearch.p.rapidapi.com/api/search"

payload = {
    "query": "Find the most viral, outrageous, or controversial IPL 2025 gossip or incident that would break the internet today. Create hyper-sensational fake news that feels so real people will argue about it in the comments. It should feel like a leaked scandal, absurd stat, or wild drama involving cricketers, owners, or fans. Format the response as follows: Headline: [Start with an explosive, highly clickable line that shocks or confuses. Use caps, emojis, slang, and exaggeration — make it look like a Reel title.] Summary: A 3–4 line Hindi explanation written like a chaotic rant or gossip. Be funny, dramatic, and unexpected. Mix Gen-Z slang, shocking punchlines, emoji reactions, and a twist. Keep the flow fast and addictive — like a friend telling you wild tea.] Music: [Suggest a currently trending music title in India (only the song name) that fits the mood of the news, based on viral Instagram/Reels trends. Format: Music: [song title].] Ensure the response is structured exactly like this, with the Hindi summary mimicking Varun Mayya’s tone—relatable, humorous, and attention-grabbing."
}
headers = {
    "x-rapidapi-key": "c66b66fd5fmsh2d1f2d4c5d0a073p17161ajsnb75f8dbbac1d",
    "x-rapidapi-host": "ai-deepsearch.p.rapidapi.com",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    response_data = response.json()

    # Extract result string directly
    result_string = response_data.get("result", "")

    # Extract headline, summary, and music using regex
    headline_match = re.search(r"Headline:\s*(.*?)\n", result_string)
    summary_match = re.search(r"Summary:\s*(.*?)\n", result_string, re.DOTALL)
    music_match = re.search(r"Music:\s*(.*?)(?=\n|$)", result_string)

    # Remove any unwanted `**` or extra formatting around the result
    headline = headline_match.group(1).strip().replace('**', '') if headline_match else "No headline found"
    summary = summary_match.group(1).strip().replace('**', '') if summary_match else "No summary found"
    full_music = music_match.group(1).strip().replace('**', '') if music_match else "No music found"
    music_words = full_music.split()
    music = ' '.join(music_words[:2]) if music_words else "No music found"

    print("Headline:", headline)
    print("Summary:", summary)
    print("Music:", music)

except requests.exceptions.RequestException as e:
    print("Error:", e)

url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/search_music"

querystring = {"search_query": music}

headers = {
    "x-rapidapi-key": "c66b66fd5fmsh2d1f2d4c5d0a073p17161ajsnb75f8dbbac1d",
    "x-rapidapi-host": "real-time-instagram-scraper-api1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    data = response.json()

    # Check if the 'data' list is not empty before accessing elements
    if data.get("data", []):
        first_track = data.get("data", [])[0].get("track", {})
        first_audio_url = first_track.get("fast_start_progressive_download_url")
        print(first_audio_url)
        cloudinary.config(
                    cloud_name="dkr5qwdjd",
                    api_key="797349366477678",
                    api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"
        )
        upload_result = cloudinary.uploader.upload(first_audio_url, resource_type="video")

                # 🔹 Print Public ID
        music_public_id = upload_result.get("public_id")
        print(f"✅ Uploaded Successfully! Public ID: {music_public_id}")
    else:
        print("No matching music found.")  # Handle the case where the list is empty
else:
    print("Error:", response.status_code, response.text)
# Extract only the first 5 words from the headline
url = "https://google-search72.p.rapidapi.com/imagesearch"

querystring = {"q": headline, "gl": "in", "lr": "lang_en", "num": "1", "start": "0"}

headers = {
    "x-rapidapi-key": "c66b66fd5fmsh2d1f2d4c5d0a073p17161ajsnb75f8dbbac1d",
    "x-rapidapi-host": "google-search72.p.rapidapi.com"
}

try:
    response = requests.get(url, params=querystring, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    image_data_list = response.json().get("items", [])  # Extract "items" safely

    if image_data_list and "thumbnailImageUrl" in image_data_list[0]:
        # Extract the thumbnail image URL
        thumbnail_url = image_data_list[0]["thumbnailImageUrl"]
        print("✅ Thumbnail Image URL:", thumbnail_url)

        # Upload image to Cloudinary
        cloudinary.config(
            cloud_name="dkr5qwdjd",
            api_key="797349366477678",
            api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"
        )
        upload_result = cloudinary.uploader.upload(thumbnail_url, folder="Mythesis_images")

        # Get image URL from Cloudinary
        public_id = upload_result.get("public_id", "").replace("/", ":")
        print("✅ Uploaded Image URL:", public_id)

    else:
        print("❌ Error: 'thumbnailImageUrl' key not found in the response or response list is empty.")
        thumbnail_url = None

except requests.exceptions.RequestException as e:
    print(f"❌ Failed to search for images: {e}")
    thumbnail_url = None

# VOICE GENERATION
summar = summary;

headers = {
    "xi-api-key": API_VOICE_KEY,
    "Content-Type": "application/json"
}

data = {
    "text": summary,
    "voice_settings": {
        "speed": 1.0,
        "stability": 0.5,
        "similarity_boost": 0.8,
        "style_exaggeration": 0.1

    },
    "model_id": "eleven_multilingual_v2",
    "output_format": "mp3"
}

response = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}", headers=headers, json=data)

if response.status_code == 200:
    print("✅ Audio Generated Successfully!")

    # ✅ Step 3: Upload Audio Directly to Cloudinary
    audio_file = response.content  # Get audio content

    upload_response = cloudinary.uploader.upload(
        file=audio_file,
        resource_type="video",  # Cloudinary treats audio files as "video"
        format="mp3",
    )
    cloudinary_url = upload_response["secure_url"]
    cloudinary_public_id = upload_response["public_id"]

    print(f"🌍 Cloudinary URL: {cloudinary_url}")
    print(f"📂 Cloudinary Public ID: {cloudinary_public_id}")
else:
    print("❌ Error Generating Audio:", response.text)


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

      {"overlay": f"audio:{cloudinary_public_id}",  "duration": "30"},
      {'effect':"volume:100"},
      {'flags': "layer_apply"},
      {'width': 500, 'crop': "scale"},

      {"overlay": f"audio:{music_public_id}", "start_offset": "45", "duration": "30"},
      {'effect':"volume:-90"},
      {'flags': "layer_apply"},
      {'width': 500, 'crop': "scale"},

      {
      'overlay': {
      'font_family': "georgia",
      'font_weight': "bold",
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
upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
payload = {
        "video_url": mp4_url,
        "caption": summary,
        "media_type": "REELS",
	      "audio_name": "S.T.A.Y.",
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


# === Step 1: Download Reel video ===
def download_file(url, filename):
    """Downloads a file from a URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Downloaded {filename} successfully!")
        return filename
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading file: {e}")
        return None


# === Step 3: YouTube Upload Helpers ===
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)

def initialize_upload(youtube, file, title, description, category, keywords, privacy_status):
    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=keywords.split(","),
            categoryId=category
        ),
        status=dict(
            privacyStatus=privacy_status
        )
    )
    media = MediaFileUpload(file, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⬆️ Uploading to YouTube: {int(status.progress() * 100)}%")
    print("🎉 YouTube upload complete!")
    return response

# === Main Execution ===
downloaded_file = download_file(mp4_url, "reel.mp4")

if downloaded_file: # Use actual upload logic

    if media_id:
        try:
            youtube = get_authenticated_service()
            initialize_upload(
                youtube,
                downloaded_file,
                title=headline,
                description=summary,
                category="22",  # People & Blogs
                keywords="instagram, reels, trending, india",
                privacy_status="public"
            )
            print("✅ Reel uploaded to YouTube successfully!")

            os.remove(downloaded_file)
        except HttpError as e:
            print(f"❌ An HTTP error occurred: {e}")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
    else:
        print("❌ Error: Instagram upload failed.")
else:
    print("❌ Error: Failed to download the Reel video.")
