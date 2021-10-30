#!/bin/bash
USERNAME="admin"
PASSWORD="admin"
IP="192.168.10.149"
TODAY=`date +%s`
DIRECTORY="Output/Pictures"
ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg