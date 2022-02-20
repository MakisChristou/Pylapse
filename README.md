## Pylapse
PyLapse is a GUI frontend written in Python 3 using the tkinter GUI framerwork. It is a frontend for the popular command line utility ffmpeg. It enables novice users to start easily capturing jpeg images from RTSP (x264) enabled cameras, save them locally and render a quick video out of them all using Pylapse.

## Features

- Capture and playback images from x264 RTSP enabled cameras
- Render video given selected dates
- Supports multiple cameras
- Multiple playback speed options
- Playback progress bar
- Timelapse running even if application is accidentally closed
- Start/End time of time-lapse (e.g. always start at 7am and end at 7PM)


## Screenshots

<img width="200" src="Screenshots/_000.png"> <img width="200" src="Screenshots/_001.png">

## Installation on Ubuntu 21.04

```
sudo apt-get install ffmpeg -y
sudo apt-get install python3-pip -y
sudo apt-get install python3-tk -y
sudo apt-get install python3-pil python3-pil.imagetk -y
pip install opencv-python
pip install tkcalendar
pip install requests
pip install --upgrade psutil
```


## Running 

`python3 main.py`

