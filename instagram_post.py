import os

print("Current working directory:", os.getcwd())
print("Files in this directory:", os.listdir())

VIDEO_PATH = "promo.mp4"
print("File exists:", os.path.exists(VIDEO_PATH))
