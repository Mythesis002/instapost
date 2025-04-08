import os

print("Current working directory:", os.getcwd())
print("Files in this directory:", os.listdir())

VIDEO_PATH = "video.MOV"
print("File exists:", os.path.exists(VIDEO_PATH))
