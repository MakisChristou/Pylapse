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


# Get user input from HTML
interval = "60"
cam_ip = "192.168.10.149"
cam_username = "admin"
cam_pass = "admin"




# Check if variables are empty
if not interval or not cam_ip or not cam_username or not cam_pass:
    print("At least one variable is empty")
    exit


# Check if interval is integer
try:
    int(interval)
except Exception as e:
    print("Invalid Interval")
    exit

# Check if user given IPs, Usernames and passwords work
cap = cv2.VideoCapture('rtsp://'+cam_username+':'+cam_pass+'@'+cam_ip+':554//h264Preview_01_main')
ret, img = cap.read()
if ret == True:
    print("RTSP Stream Succesful")
    # im = Image.fromarray(img)
    # im.save("camera1.jpeg")
else:
    print("Cannot connect to camera")
    exit
    
cap.release()
cv2.destroyAllWindows()


# Write to file (for timelapse.sh script)
render_settings_file = open("timelapse_settings.txt", "w")
render_settings_file.write(interval+"\n")
render_settings_file.write(cam_ip+"\n")
render_settings_file.write(cam_username+"\n")
render_settings_file.write(cam_pass+"\n")
render_settings_file.close()


command = ['pgrep', 'timelapse.sh']
result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

# So we don't expode the server
# Stop if rendering script is running already for some reason
if result.stdout:
    print("timelapse.sh script is already running, exiting")
    exit
else:
    print("timelapse.sh script not running, continuing")


print(subprocess.run(["./timelapse.sh"], shell=False))