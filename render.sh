#!/bin/bash

LOG_FILE="output.txt"
FILENAME="out"
RENDER_SETTINGS_FILE="render_settings.txt"
START_DATE=$(sed '1q;d' $RENDER_SETTINGS_FILE)
END_DATE=$(sed '2q;d' $RENDER_SETTINGS_FILE)
FRAMERATE=$(sed '3q;d' $RENDER_SETTINGS_FILE)
FILENAME=$START_DATE--$END_DATE

ffmpeg -y -progress output.txt -framerate $FRAMERATE -pattern_type glob -i "temp/*.jpeg" -c:v libx264 -r $FRAMERATE -pix_fmt yuv420p "Output/Videos"/$FILENAME.mp4 #1> $LOG_FILE 2>&1