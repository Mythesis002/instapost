import os
import time
import random
import google.auth
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
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


def get_authenticated_service():
    """Authenticate and get the YouTube service."""
    creds = None
    # Load saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If credentials are not available, request new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"Please go to this URL: {auth_url}")

            code = input("Enter the authorization code: ")
            creds = flow.fetch_token(code=code)


        # Save the credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)   

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def initialize_upload(youtube, file_path, title, description, category, keywords, privacy_status):
    """Upload the video to YouTube."""
    tags = keywords.split(",") if keywords else None

    # Video metadata
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category,
        },
        "status": {"privacyStatus": privacy_status},
    }

    # Upload video file
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    resumable_upload(request)


def resumable_upload(request):
    """Handle resumable uploads with retries."""
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print("Uploading file...")
            status, response = request.next_chunk()
            if response is not None and "id" in response:
                print(f"✅ Video uploaded successfully! Video ID: {response['id']}")
                return
            else:
                print(f"❌ Upload failed: {response}")
                return
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                print("❌ Max retries reached. Upload failed.")
                return
            sleep_seconds = random.random() * (2 ** retry)
            print(f"🔄 Retrying in {sleep_seconds:.2f} seconds...")
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    # Define video details
    video_file = "video.MOV"  # Replace with actual file path
    video_title = "My YouTube Video"
    video_description = "This is an uploaded video using YouTube API."
    video_category = "22"  # Category ID (e.g., 22 = People & Blogs)
    video_keywords = "test,upload,youtube"
    video_privacy = "public"  # Options: public, private, unlisted

    # Check if the file exists
    if not os.path.exists(video_file):
        print("❌ Error: Video file not found!")
        exit()

    # Authenticate and upload
    youtube_service = get_authenticated_service()
    initialize_upload(youtube_service, video_file, video_title, video_description, video_category, video_keywords, video_privacy)
