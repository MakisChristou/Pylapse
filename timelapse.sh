#!/bin/bash
while [ ! -f .stop ]
do
    start=`date +%s`
    DIRECTORY="Output/Pictures"
    TIMELAPSE_SETTINGS_FILE="timelapse_settings.txt"
    INTERVAL=$(sed '1q;d' $TIMELAPSE_SETTINGS_FILE)
    INTERVAL=$(echo $INTERVAL | base64 --decode)
    IP=$(sed '2q;d' $TIMELAPSE_SETTINGS_FILE)
    IP=$(echo $IP | base64 --decode)
    USERNAME=$(sed '3q;d' $TIMELAPSE_SETTINGS_FILE)
    USERNAME=$(echo $USERNAME | base64 --decode)
    PASSWORD=$(sed '4q;d' $TIMELAPSE_SETTINGS_FILE)
    PASSWORD=$(echo $PASSWORD | base64 --decode)
    TIME_START=$(sed '5q;d' $TIMELAPSE_SETTINGS_FILE)
    TIME_START=$(echo $TIME_START | base64 --decode)
    TIME_END=$(sed '6q;d' $TIMELAPSE_SETTINGS_FILE)
    TIME_END=$(echo $TIME_END | base64 --decode)
    IFS=',' read -ra IPS <<< "$IP"
    IFS=',' read -ra USERNAMES <<< "$USERNAME"
    IFS=',' read -ra PASSWORDS <<< "$PASSWORD"
    SIZE=${#IPS[@]}
    CURRENT_TIME=$(date +%H%M)
    TODAY=`date +%s`
    if [ $CURRENT_TIME -lt $TIME_END ] && [ $TIME_START -lt $CURRENT_TIME ]
    then
        for ((i = 0 ; i < $SIZE ; i++)); do
            #echo "Counter: $i"
            SAVE_DIRECTORY="Output/Pictures/Camera"$i
            #echo $SAVE_DIRECTORY
            ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://${USERNAMES[i]}:${PASSWORDS[i]}@${IPS[i]}//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $SAVE_DIRECTORY/$TODAY.jpeg
        done
        #exit
    fi
    end=`date +%s`
    runtime=$((end-start))
    sleep $((INTERVAL-runtime))
done
#ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg