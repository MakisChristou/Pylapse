import os
import subprocess
from subprocess import Popen, PIPE, run
import requests
from wsgiref.util import FileWrapper
import cv2
import psutil
import datetime
import shutil
from PIL import Image


command = ['pgrep', 'render.sh']
result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

# So we don't expode the server
# Stop if rendering script is running already for some reason
if result.stdout:
    print("render.sh script is already running, exiting")
    exit
else:
    print("render.sh script not running, continuing")


start_date = "15/10/2021"
end_date = "17/10/2021"
framerate = "30"


# Check if variables are empty
if not start_date or not end_date or not framerate:
    print("At least one variable is empty")
    exit

# Convert user input to date object and catch potential exceptions
try:
    start_date_object = datetime.datetime.strptime(start_date,"%d/%m/%Y")
    end_date_object = datetime.datetime.strptime(end_date+" 23:59:59","%d/%m/%Y %H:%M:%S")
except Exception as e:
    print("Wrong date format")
    exit

# Check if framerate is integer
try:
    int(framerate)
except Exception as e:
    print("Wrong framerate")
    exit


# Write to file (for render.sh script)
render_settings_file = open("render_settings.txt", "w")
render_settings_file.write(start_date.replace("/", "-")+"\n")
render_settings_file.write(end_date.replace("/", "-")+"\n")
render_settings_file.write(framerate+"\n")
render_settings_file.close()


pictures = os.listdir(path='Output/Pictures')

picture_count = 0

# Make sure temp dir is empty
if os.path.isdir("temp"):
    shutil.rmtree("temp")

os.mkdir("temp")

print("Copying files to temp dir")

for file in pictures:
    unix_epoch = file[0:10]
    temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
    if temp_date_object > start_date_object and temp_date_object < end_date_object:
        picture_count+=1
        shutil.copy("Output/Pictures/"+file, "temp")


print("Timelapse will be composed of ", picture_count, " pictures")

# Render if we have pictures
if picture_count >= 1:
    print("Rendering using ffmpeg")
    # Start Rendering
    print(subprocess.run(["./render.sh"], shell=False))


# Remove temp directory
if os.path.isdir("temp"):
    shutil.rmtree("temp")
