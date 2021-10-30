#!/bin/bash

DIRECTORY="Output/Pictures"
TIMELAPSE_SETTINGS_FILE="timelapse_settings.txt"
IP=$(sed '2q;d' $TIMELAPSE_SETTINGS_FILE)
USERNAME=$(sed '3q;d' $TIMELAPSE_SETTINGS_FILE)
PASSWORD=$(sed '4q;d' $TIMELAPSE_SETTINGS_FILE)
ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg