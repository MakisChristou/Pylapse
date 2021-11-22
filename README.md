# Features

- Caputre and playback images from RTSP enabled cameras
- Render video given selected dates
- Supports multiple cameras
- Password protected timelapse settings
- Multiple playback speed options
- Playback progress bar
- Timelapse running even if application is accidentally closed
- Start/End time of time-lapse (e.g. always start at 7am and end at 7PM)


## Screenshots

<img width="200" src="Screenshots/_000.png"> <img width="200" src="Screenshots/_001.png"> <img width="200" src="Screenshots/_002.png"> <img width="200" src="Screenshots/_003.png">
<img width="200" src="Screenshots/_004.png"> <img width="200" src="Screenshots/_005.png"> <img width="200" src="Screenshots/_006.png"> <img width="200" src="Screenshots/_007.png">



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

