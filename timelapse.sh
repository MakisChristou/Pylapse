#!/bin/bash

DIRECTORY="Output/Pictures"
TIMELAPSE_SETTINGS_FILE="timelapse_settings.txt"
IP=$(sed '2q;d' $TIMELAPSE_SETTINGS_FILE)
USERNAME=$(sed '3q;d' $TIMELAPSE_SETTINGS_FILE)
PASSWORD=$(sed '4q;d' $TIMELAPSE_SETTINGS_FILE)
TODAY=`date +%s`


IFS=',' read -ra IPS <<< "$IP"
IFS=',' read -ra USERNAMES <<< "$USERNAME"
IFS=',' read -ra PASSWORDS <<< "$PASSWORD"

echo ${IPS[1]}
echo ${USERNAMES[1]}
echo ${PASSWORDS[1]}

SIZE=${#IPS[@]}

echo $SIZE

for ((i = 0 ; i < $SIZE ; i++)); do
    #echo "Counter: $i"
    SAVE_DIRECTORY="Output/Pictures/Camera"$i
    #echo $SAVE_DIRECTORY
    ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://${USERNAMES[i]}:${PASSWORDS[i]}@${IPS[i]}//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $SAVE_DIRECTORY/$TODAY.jpeg

done



#exit
#ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg
