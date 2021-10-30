#!/bin/bash

INTERVAL=60 #Note that it takes ~5 seconds to actually get the screenshot
DIRECTORY1="Output"
DIRECTORY2="Pictures"
TODAY=`"date" +"(%D)""(%T)"`
USERNAME="admin"
PASSWORD="admin"
IP="192.168.10.149"
DAILY_START_TIME=""
DAILY_END_TIME=""
START_DATE=""
END_DATE=""
TIMELAPSE_SETTINGS_FILE="timelapse_settings.txt"


# If script already running exit
#if [[ "`pidof -x $(basename $0) -o %PPID`" ]]; then exit; fi

# Example Usage
# ./timelapse.sh admin admin 192.168.10.149


# if timelapse settings available use them otherwise use defaults
if test -f "$TIMELAPSE_SETTINGS_FILE";
then
	echo "$TIMELAPSE_SETTINGS_FILE exists."
    INTERVAL=$(sed '1q;d' $TIMELAPSE_SETTINGS_FILE)
else
	INTERVAL=60
	USERNAME="admin"
	PASSWORD="admin"
	IP="192.168.10.149"
fi

usernames=('admin')
passwords=('admin')
ips=('192.168.10.149')

echo "Interval $INTERVAL"
echo "usernames $usernames"
echo "passwords $passwords"
echo "ips $ips"

FIRST_USERNAME=${usernames[0]}

echo $FIRST_USERNAME

# exit

DIRECTORY=$DIRECTORY1/$DIRECTORY2 # DIRECTORY="Output/Pictures"


if [ ! -d "$DIRECTORY" ]; then
  # Control will enter here if $DIRECTORY doesn't exist.
	mkdir $DIRECTORY1
	cd $DIRECTORY1
	mkdir $DIRECTORY2
	cd ..
fi

# http://$IP/cgi-bin/api.cgi?cmd=Snap&channel=0&user=$USERNAME&password=$PASSWORD
# ffmpeg -ss 2 -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg


while [ true ]
do
	TODAY=`date +%s`
	ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg
	sleep $INTERVAL
done


