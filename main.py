import tkinter as tk
from tkinter import filedialog, Text
import os
import subprocess
from subprocess import Popen, PIPE, run
import requests
from wsgiref.util import FileWrapper
import cv2
import psutil
import datetime
import shutil
from tkinter import *
from PIL import Image,ImageTk
from tkcalendar import Calendar, DateEntry
import datetime
import time
from tkinter import messagebox
from tkinter.ttk import Progressbar
from time import sleep
import tempfile
import threading
import signal
import re
import sys
import base64
import timeit


root = tk.Tk()
root.title("Timelapse not running")
root.resizable(width=False, height=False)

user_choice = ""
picture_count = 0
interval=10
playbackThread = threading.Thread()
renderingThread = threading.Thread()
timelapseThread = threading.Thread()
statusThread = threading.Thread()
deleteThread = threading.Thread()
errorCheckThread = threading.Thread()

ips = [] # Filled in loadTimelapseSettings()
usernames = [] # Filled in loadTimelapseSettings()
passwords = [] # Filled in loadTimelapseSettings()
cameras = [] # Filled in loadTimelapseSettings()


camera_ips = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()
camera_usernames = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()
camera_passwords = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()
camera_interval = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()
camera_start_hour = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()
camera_end_hour = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()
camera_store_last = "" # Filled either in readTimelapseSettings() or saveTimelapseSettings()

current_playback_image = 0

# Create empty process for global use
rendering_process = None

# start_date_cal = DateEntry()
# end_date_cal = DateEntry()

# Declare as global variable
log_file = None


settings_password = "agathangelou"


def kill_process(name):
     
    # Ask user for the name of process
    try:
         
        # iterating through each instance of the process
        for line in os.popen("ps ax | grep " + name + " | grep -v grep"):
            fields = line.split()
             
            # extracting Process ID from the output
            pid = fields[0]
             
            # terminating process
            os.kill(int(pid), signal.SIGKILL)
        print(str(datetime.datetime.now()), "Script Successfully terminated")
        messagebox.showinfo("Success", "Script successfully terminated")
         
    except:
        print(str(datetime.datetime.now()), "Script could not be successfully terminated")
        messagebox.showerror("Error", "Script could not be successfully terminated")

# Loads first image on canvas (by default loads first image for today)
def loadFirstImage():

    global start_date_cal
    global end_date_cal
    global label

    print(str(datetime.datetime.now()), start_date_cal)
    print(str(datetime.datetime.now()), end_date_cal)


    return 

# Writes internal string data structures in the timelapse_settings.txt file
def writeTimelapseSettings():

    global camera_ips
    global camera_usernames
    global camera_passwords
    global camera_interval
    global camera_start_hour
    global camera_end_hour
    global camera_store_last

    # Remove whitespace from strings
    camera_ips = re.sub(r"\s+", "", camera_ips, flags=re.UNICODE)
    camera_usernames = re.sub(r"\s+", "", camera_usernames, flags=re.UNICODE)
    camera_passwords = re.sub(r"\s+", "", camera_passwords, flags=re.UNICODE)
    camera_interval = re.sub(r"\s+", "", camera_interval, flags=re.UNICODE)
    camera_start_hour = re.sub(r"\s+", "", camera_start_hour, flags=re.UNICODE)
    camera_end_hour = re.sub(r"\s+", "", camera_end_hour, flags=re.UNICODE)
    camera_store_last = re.sub(r"\s+", "", camera_store_last, flags=re.UNICODE)


    print(str(datetime.datetime.now()), "loadTimelapseSettings()")
    print(str(datetime.datetime.now()), camera_ips)
    print(str(datetime.datetime.now()), camera_usernames)
    print(str(datetime.datetime.now()), camera_passwords)
    print(str(datetime.datetime.now()), camera_interval)
    print(str(datetime.datetime.now()), camera_start_hour)
    print(str(datetime.datetime.now()), camera_end_hour)
    print(str(datetime.datetime.now()), camera_store_last)


    # Check if empty variables
    if not camera_interval or not camera_usernames or not camera_passwords:
        print(str(datetime.datetime.now()), "Some variables are empty")
        messagebox.showerror("Error", "Wrong timelapse_settings.txt format")
        return

    # Check if interval is integer
    try:
        int(camera_interval)
    except Exception as e:
        print(str(datetime.datetime.now()), "Invalid Interval")
        messagebox.showerror("Error", "Interval must be an integer")
        return

    # Get number of commas
    a = camera_ips.count(',')
    b = camera_usernames.count(',')
    c = camera_passwords.count(',')

    # Check that ips, usernames and passwords have the same commas
    if a != b or a != c or c != b:
        print(str(datetime.datetime.now()), "Wrong timelapse_settings.txt format")
        messagebox.showerror("Error", "Wrong timelapse_settings.txt format")
        return




    # Encrypt passwords
    try:
        encrypted_camera_ips = trivial_encrypt(camera_ips)
        encrypted_camera_usernames = trivial_encrypt(camera_usernames)
        encrypted_camera_passwords = trivial_encrypt(camera_passwords)
        encrypted_camera_interval = trivial_encrypt(camera_interval)
        encrypted_camera_start_hour = trivial_encrypt(camera_start_hour)
        encrypted_camera_end_hour = trivial_encrypt(camera_end_hour)
        encrypted_camera_store_last = trivial_encrypt(camera_store_last)
    except Exception as e:
        print(str(datetime.datetime.now()), "Cannot encrypt timelapse settings")
        messagebox.showerror("Error", "Cannot encrypt timelapse settings")
        return

    # Write to file (for timelapse.sh script)
    timelapse_settings_file = open("timelapse_settings.txt", "w")
    timelapse_settings_file.write(encrypted_camera_interval+"\n")
    timelapse_settings_file.write(encrypted_camera_ips+"\n")
    timelapse_settings_file.write(encrypted_camera_usernames+"\n")
    timelapse_settings_file.write(encrypted_camera_passwords+"\n")
    timelapse_settings_file.write(encrypted_camera_start_hour+"\n")
    timelapse_settings_file.write(encrypted_camera_end_hour+"\n")
    timelapse_settings_file.write(encrypted_camera_store_last+"\n")
    timelapse_settings_file.close()

# Base64 decode
def trivial_decrypt(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message

# Base64 encode
def trivial_encrypt(message):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

# loads lits data structures from string data structures
def loadTimelapseSettings():

    global camera_ips
    global camera_usernames
    global camera_passwords
    global camera_interval
    global camera_start_hour
    global camera_end_hour
    global camera_store_last

    global ips
    global usernames
    global passwords
    global cameras

    # Remove whitespace from strings
    camera_ips = re.sub(r"\s+", "", camera_ips, flags=re.UNICODE)
    camera_usernames = re.sub(r"\s+", "", camera_usernames, flags=re.UNICODE)
    camera_passwords = re.sub(r"\s+", "", camera_passwords, flags=re.UNICODE)
    camera_interval = re.sub(r"\s+", "", camera_interval, flags=re.UNICODE)
    camera_start_hour = re.sub(r"\s+", "", camera_start_hour, flags=re.UNICODE)
    camera_end_hour = re.sub(r"\s+", "", camera_end_hour, flags=re.UNICODE)
    camera_store_last = re.sub(r"\s+", "", camera_store_last, flags=re.UNICODE)   

    print(str(datetime.datetime.now()), "loadTimelapseSettings()")
    print(str(datetime.datetime.now()), camera_ips)
    print(str(datetime.datetime.now()), camera_usernames)
    print(str(datetime.datetime.now()), camera_passwords)
    print(str(datetime.datetime.now()), camera_interval)
    print(str(datetime.datetime.now()), camera_start_hour)
    print(str(datetime.datetime.now()), camera_end_hour)
    print(str(datetime.datetime.now()), camera_store_last)

    # Check if empty variables
    if not camera_interval or not camera_usernames or not camera_passwords:
        print(str(datetime.datetime.now()), "Some variables are empty")
        messagebox.showerror("Error", "Wrong timelapse_settings.txt format")
        return 1

    # Check if interval is integer
    try:
        int(camera_interval)
    except Exception as e:
        print(str(datetime.datetime.now()), "Invalid Interval")
        messagebox.showerror("Error", "Interval must be an integer")
        return 1

    # Check if start time is integer
    try:
        int(camera_start_hour)
    except Exception as e:
        print(str(datetime.datetime.now()), "Invalid Start Hour")
        messagebox.showerror("Error", "Start Hour must be an integer")
        return 1

    # Check if start time is integer
    try:
        int(camera_end_hour)
    except Exception as e:
        print(str(datetime.datetime.now()), "Invalid End Hour")
        messagebox.showerror("Error", "End Hour must be an integer")
        return 1

    # Check if number of months is integer
    try:
        int(camera_store_last)
    except Exception as e:
        print(str(datetime.datetime.now()), "Invalid Months to store")
        messagebox.showerror("Error", "Months to store must be an integer")
        return 1

    if int(camera_store_last) < 0:
        print(str(datetime.datetime.now()), "Invalid Months to store")
        messagebox.showerror("Error", "Months to store must be positive")
        return 1


    if int(camera_start_hour) < 0 or int(camera_start_hour) > 2359:
        print(str(datetime.datetime.now()), "Invalid Start Hour")
        messagebox.showerror("Error", "Invalid Start Hour, modify timelapse settings")
        return 1

    if int(camera_end_hour) < 0 or int(camera_end_hour) > 2359:
        print(str(datetime.datetime.now()), "Invalid End Hour")
        messagebox.showerror("Error", "Invalid End Hour, modify timelapse settings")
        return 1

    # Get number of commas
    a = camera_ips.count(',')
    b = camera_usernames.count(',')
    c = camera_passwords.count(',')

    # Check that ips, usernames and passwords have the same commas
    if a != b or a != c or c != b:
        print(str(datetime.datetime.now()), "Wrong timelapse_settings.txt format")
        messagebox.showerror("Error", "Wrong timelapse_settings.txt format")
        return 1


    # Clear so we don't have duplicates
    ips.clear()
    usernames.clear()
    passwords.clear()
    cameras.clear()

    # Construct ips global list
    temp = ""
    for char in camera_ips:
        if char == ",":
            print(str(datetime.datetime.now()), "Yes")
        if char == ',':
            ips.append(temp)
            temp = ""
        if char != ",":
            temp+=char
    ips.append(temp)


    # Construct usernames global list
    temp = ""
    for char in camera_usernames:
        if char == ',':
            usernames.append(temp)
            temp = ""
        
        if char != ",":
            temp+=char
    usernames.append(temp)


    # Construct passwords global list
    temp = ""
    for char in camera_passwords:
        if char == ',':
            passwords.append(temp)
            temp = ""
        
        if char != ",":
            temp+=char
    passwords.append(temp)


    for i in range(len(ips)):
        cameras.append(i)

    return 0

# Test if timelapse file exists, if so save results in global variables
def readTimelapseSettings():

    # Attempt to read timelapse_settings.txt
    file_exists = os.path.exists("timelapse_settings.txt")

    global camera_ips
    global camera_usernames
    global camera_passwords
    global camera_interval
    global camera_start_hour
    global camera_end_hour
    global camera_store_last


    if file_exists:
        f = open("timelapse_settings.txt","r")
        lines = f.readlines()
        camera_interval = lines[0]
        camera_ips = lines[1]
        camera_usernames = lines[2]
        camera_passwords = lines[3]
        camera_start_hour = lines[4]
        camera_end_hour = lines[5]
        camera_store_last = lines[6]


        # Decrypt Passwords
        try:
            camera_interval = trivial_decrypt(camera_interval)
            camera_ips = trivial_decrypt(camera_ips)
            camera_usernames = trivial_decrypt(camera_usernames)
            camera_passwords = trivial_decrypt(camera_passwords)
            camera_start_hour = trivial_decrypt(camera_start_hour)
            camera_end_hour = trivial_decrypt(camera_end_hour)
            camera_store_last = trivial_decrypt(camera_store_last)
        except Exception as e:
            print(str(datetime.datetime.now()), "Cannot decrypt timelapse settings")
            messagebox.showerror("Error", "Cannot decrypt timelapse settings")
            return 1
        


        # Check if variables are empty
        if len(lines) != 7:
            messagebox.showerror("Error", "Wrong timelapse_settings.txt format")
            return 1


        # List data structures are filled 
        return loadTimelapseSettings()

    else:
        messagebox.showerror("Error", "timelapse_settings.txt file does not exist")
        return 1

    print(str(datetime.datetime.now()), ips)
    print(str(datetime.datetime.now()), usernames)
    print(str(datetime.datetime.now()), passwords)
    return 0

# Test if all of the cameras are reachable via RTSP (returns 1 if fail and 0 if success)
def testRTSPCameras():

    # For each camera
    for i in range(len(ips)):
        # Check if user given IPs, Usernames and passwords work
        cap = cv2.VideoCapture('rtsp://'+usernames[i]+':'+passwords[i]+'@'+ips[i]+':554//h264Preview_01_main')
        ret, img = cap.read()
        if ret == True:
            print(str(datetime.datetime.now()), "RTSP Stream " + str(i) + " Succesful")
            # messagebox.showinfo("Success", "Camera is reachable via RTSP")
            # im = Image.fromarray(img)
            # im.save("camera1.jpeg")
        else:
            print(str(datetime.datetime.now()), "Cannot connect to camera")
            messagebox.showerror("Error", "Camera " + str(i) + " is not reachable via RTSP")
            return 1


    messagebox.showinfo("Success", "Cameras are reachable via RTSP")
    return 0

# Write timelapse settings to its relevant text file
def timelapseSettings():

    def saveTimelapseSettings():

        global camera_ips
        global camera_usernames
        global camera_passwords
        global camera_interval
        global camera_start_hour
        global camera_end_hour
        global camera_store_last


        # Get data from text boxes
        camera_ips = IPInputText.get(1.0, "end-1c")
        camera_usernames = useranameInputText.get(1.0, "end-1c")
        camera_passwords = passwordInputText.get(1.0, "end-1c")
        camera_interval = intervalInputText.get(1.0, "end-1c")
        camera_start_hour = startHourInputText.get(1.0, "end-1c")
        camera_end_hour = endHourInputText.get(1.0, "end-1c")
        camera_store_last = storeLastInputText.get(1.0, "end-1c")


        # Remove whitespace from strings
        camera_ips = re.sub(r"\s+", "", camera_ips, flags=re.UNICODE)
        camera_usernames = re.sub(r"\s+", "", camera_usernames, flags=re.UNICODE)
        camera_passwords = re.sub(r"\s+", "", camera_passwords, flags=re.UNICODE)
        camera_interval = re.sub(r"\s+", "", camera_interval, flags=re.UNICODE)
        camera_start_hour = re.sub(r"\s+", "", camera_start_hour, flags=re.UNICODE)
        camera_end_hour = re.sub(r"\s+", "", camera_end_hour, flags=re.UNICODE)
        camera_store_last = re.sub(r"\s+", "", camera_store_last, flags=re.UNICODE)


        print(str(datetime.datetime.now()), "SaveTimelapseSettings()")
        print(str(datetime.datetime.now()), camera_ips)
        print(str(datetime.datetime.now()), camera_usernames)
        print(str(datetime.datetime.now()), camera_passwords)
        print(str(datetime.datetime.now()), camera_interval)
        print(str(datetime.datetime.now()), camera_start_hour)
        print(str(datetime.datetime.now()), camera_end_hour)
        print(str(datetime.datetime.now()), camera_store_last)


        # List data structures are filled, don't bother saving incorrect stuff
        quit = loadTimelapseSettings()
        if quit == 1:
            return

        # Check data validity
        quit = testRTSPCameras()

        # Quit if RTSP is not reachable
        if quit == 1:
            return
        else:
            # Save file

            try:
                encrypted_camera_ips = trivial_encrypt(camera_ips)
                encrypted_camera_usernames = trivial_encrypt(camera_usernames)
                encrypted_camera_passwords = trivial_encrypt(camera_passwords)
                encrypted_camera_interval = trivial_encrypt(camera_interval)
                encrypted_camera_start_hour = trivial_encrypt(camera_start_hour)
                encrypted_camera_end_hour = trivial_encrypt(camera_end_hour)
                encrypted_camera_store_last = trivial_encrypt(camera_store_last)

            except Exception as e:
                print(str(datetime.datetime.now()), "Cannot encrypt timelapse settings")
                messagebox.showerror("Error", "Cannot encrypt timelapse settings")
                return


            # Write to file (for timelapse.sh script)
            timelapse_settings_file = open("timelapse_settings.txt", "w")
            timelapse_settings_file.write(encrypted_camera_interval+"\n")
            timelapse_settings_file.write(encrypted_camera_ips+"\n")
            timelapse_settings_file.write(encrypted_camera_usernames+"\n")
            timelapse_settings_file.write(encrypted_camera_passwords+"\n")
            timelapse_settings_file.write(encrypted_camera_start_hour+"\n")
            timelapse_settings_file.write(encrypted_camera_end_hour+"\n")
            timelapse_settings_file.write(encrypted_camera_store_last+"\n")
            timelapse_settings_file.close()
            print(str(datetime.datetime.now()), "New Settings ")
            print(str(datetime.datetime.now()), camera_interval)
            print(str(datetime.datetime.now()), camera_ips)
            print(str(datetime.datetime.now()), camera_usernames)
            print(str(datetime.datetime.now()), camera_passwords)
            print(str(datetime.datetime.now()), camera_start_hour)
            print(str(datetime.datetime.now()), camera_end_hour)
            print(str(datetime.datetime.now()), camera_store_last)
            print(str(datetime.datetime.now()), "Saved in file ")
            print(str(datetime.datetime.now()), encrypted_camera_interval)
            print(str(datetime.datetime.now()), encrypted_camera_ips)
            print(str(datetime.datetime.now()), encrypted_camera_usernames)
            print(str(datetime.datetime.now()), encrypted_camera_passwords)
            print(str(datetime.datetime.now()), encrypted_camera_start_hour)
            print(str(datetime.datetime.now()), encrypted_camera_end_hour)
            print(str(datetime.datetime.now()), encrypted_camera_store_last)
            print(str(datetime.datetime.now()), "Saved timelapse settings")
            messagebox.showinfo("Success", "Saved timelapse settings")
            messagebox.showinfo("Success", "Restart program for settings to take full effect")
        return
    

    # Saves results in global variables
    readTimelapseSettings()

    popup = tk.Toplevel()
    popup.geometry("400x400")
    tk.Label(popup, text="Camera IPs").grid(row=0,column=0)
    # TextBox Creation
    IPInputText = tk.Text(popup, height = 1, width =50) 
    IPInputText.grid(row=2,column=0)
    IPInputText.insert(END,camera_ips)

    # IPInputText.insert(0, "This is the default text")

    tk.Label(popup, text="Useranmes").grid(row=3,column=0)
    useranameInputText = tk.Text(popup, height = 1, width = 50) 
    useranameInputText.grid(row=4,column=0)
    useranameInputText.insert(END, camera_usernames)


    tk.Label(popup, text="Passwords").grid(row=5,column=0)
    passwordInputText = tk.Text(popup, height = 1, width = 50) 
    passwordInputText.grid(row=6,column=0)
    passwordInputText.insert(END,camera_passwords)

    tk.Label(popup, text="Interval (seconds)").grid(row=7,column=0)
    intervalInputText = tk.Text(popup, height = 1, width = 20) 
    intervalInputText.grid(row=8,column=0)
    intervalInputText.insert(END,camera_interval)

    tk.Label(popup, text="Start (hour)").grid(row=9,column=0)
    startHourInputText = tk.Text(popup, height = 1, width = 20) 
    startHourInputText.grid(row=10,column=0)
    startHourInputText.insert(END,camera_start_hour)

    tk.Label(popup, text="End (hour)").grid(row=11,column=0)
    endHourInputText = tk.Text(popup, height = 1, width = 20) 
    endHourInputText.grid(row=12,column=0)
    endHourInputText.insert(END,camera_end_hour)

    tk.Label(popup, text="Store Last (months)").grid(row=13,column=0)
    storeLastInputText = tk.Text(popup, height = 1, width = 20) 
    storeLastInputText.grid(row=14,column=0)
    storeLastInputText.insert(END,camera_store_last)



    saveButton = tk.Button(popup, text = "Save", command = saveTimelapseSettings)
    saveButton.grid(row=15, column=0)




    return

# Check if video has been rendered succesfully, notify User if error or not
def checkRender(picture_count):
    # Read ffmpeg output and deduce whether succeess or not
    for line in reversed(list(open("output.txt"))):
        if line.rstrip().startswith("frame="):
            
            ffmpeg_frames_rendered=line.rstrip()[6::]

            print(str(datetime.datetime.now()), ffmpeg_frames_rendered)
            print(str(datetime.datetime.now()), picture_count)

            if ffmpeg_frames_rendered == str(picture_count):
                messagebox.showinfo("Success", "Video has been successfully rendered")
            else:
                messagebox.showerror("Error", "Video has not rendered successfully")
            break

# Deletes files in temp dir to shrink duration
def chooseDuration(picture_count):
    # Helper function for duration user choice
    def ok():
        global user_choice
        user_choice = variable.get()
        popup.destroy()

    # Render in the correct duration
    duration_immutable = picture_count/30 # in seconds
    duration = duration_immutable
    smallest_duration = 10 # No video can be smaller than 5 seconds

    durations = []
    i=2

    if duration < smallest_duration:
        messagebox.showerror("Error", "Not enough pictures for minimum duration ("+str(smallest_duration)+" seconds)")
        return

    while duration >= smallest_duration:
        durations.append(int(duration))
        duration = duration_immutable / i
        i+=1

    

    # Popup window for duration options
    popup = tk.Toplevel()
    popup.title('Choose Duration')
    popup.geometry("300x100")
    variable = StringVar(popup)
    variable.set(durations[0]) # default value

    w = OptionMenu(popup, variable, *durations)
    w.config(width=12)
    w.pack()

    button = Button(popup, text="OK", command=ok)
    button.pack()

    # Pause execution until user chooses duration
    root.wait_window(popup)

    # If user doesn't input duration and just closes window
    if not user_choice:
        return -1

    keep_one_every = durations.index(int(user_choice))+1

    print(str(datetime.datetime.now()), "User choice is ", user_choice)
    print(str(datetime.datetime.now()), "Keeping one every ", keep_one_every, " pictures")
    print(str(datetime.datetime.now()), "Durations are ", durations)
    print(str(datetime.datetime.now()), "Timelapse will be composed of ", picture_count, " pictures")


    # Remove files from temporary directory to match user desired duration
    temp_pictures = os.listdir(path='temp')
    counter = 1
    for file in temp_pictures:
        
        file_path="temp/"+file

        if not ((counter % keep_one_every) == 0):
            os.remove(file_path)
            picture_count-=1
        
        counter+=1


    print(str(datetime.datetime.now()), "Timelapse will be composed of ", picture_count, " pictures")

    return picture_count

# Bonus ability because of Agathangelou requirements
def renderVideo():
    # Checks if render.sh script is running
    command = ['pgrep', 'render.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # Stop if rendering script is running already for some reason (So we don't expode the server)
    if result.stdout:
        print(str(datetime.datetime.now()), "render.sh script is already running, exiting")
        messagebox.showerror("Error", "render.sh script is already running")
        return
    else:
        print(str(datetime.datetime.now()), "render.sh script not running, continuing")


    # Check if we have the target folder to render to
    quit = checkDirectories()

    # Quit if folder structure has been modified since starting the program
    if quit == 1:
        return

    # print(str(datetime.datetime.now()), type(start_date_cal.get_date()))
    # print(str(datetime.datetime.now()), str(start_date_cal.get_date().year))

    # Check if dates were given correctly
    if start_date_cal.get_date() > end_date_cal.get_date():
        messagebox.showerror("Error", "Start date must be before end date")
        return


    # Convert them to strings because of bad life choices
    start_date = str(start_date_cal.get_date().day)+"/"+str(start_date_cal.get_date().month)+"/"+str(start_date_cal.get_date().year) # e.g. start_date "15/10/2021"
    end_date = str(end_date_cal.get_date().day)+"/"+str(end_date_cal.get_date().month)+"/"+str(end_date_cal.get_date().year) # e.g. start_date "17/10/2021"
    framerate = "30"



    # Check if variables are empty (Not gonna happen but I had this coded up so ohh well)
    if not start_date or not end_date or not framerate:
        print(str(datetime.datetime.now()), "At least one variable is empty")
        messagebox.showerror("Error", "At least one variable is empty")
        return

    # Convert user input to date object and catch potential exceptions (Not gonna happen but I had this coded up so ohh well)
    try:
        start_date_object = datetime.datetime.strptime(start_date,"%d/%m/%Y")
        end_date_object = datetime.datetime.strptime(end_date+" 23:59:59","%d/%m/%Y %H:%M:%S")
    except Exception as e:
        print(str(datetime.datetime.now()), "Wrong date format")
        messagebox.showerror("Error", "Wrong date format")
        return

    # Check if framerate is integer (Not gonna happen but I had this coded up so ohh well)
    try:
        int(framerate)
    except Exception as e:
        print(str(datetime.datetime.now()), "Wrong framerate")
        messagebox.showerror("Error", "Wrong framerate")
        return


    print(str(datetime.datetime.now()), "Camera Selection: " + camera_selection.get())

    # If this is null, quit
    if camera_selection:

        # Write to file (for render.sh script)
        render_settings_file = open("render_settings.txt", "w")
        render_settings_file.write(start_date.replace("/", "-")+"\n")
        render_settings_file.write(end_date.replace("/", "-")+"\n")
        render_settings_file.write(framerate+"\n")
        render_settings_file.write(camera_selection.get()+"\n")
        render_settings_file.close()


        picture_count = 0
        # Make sure temp dir is empty
        if os.path.isdir("temp"):
            shutil.rmtree("temp")

        os.mkdir("temp")

        camera_directory = 'Output/Pictures/Camera'+camera_selection.get()

        # Check if camera directory exists
        if not os.path.exists(camera_directory):
            print(str(datetime.datetime.now()), camera_directory + " does not exist")
            messagebox.showerror("Error", camera_directory + " does not exist")
            return


        pictures = os.listdir(path='Output/Pictures/Camera'+camera_selection.get())


        # print(str(datetime.datetime.now()), pictures)
        # Why do I have to do this? (bug)
        # pictures.remove(".jpeg")

        print(str(datetime.datetime.now()), "Copying files to temp dir")

        # Copy everyting to temp dir
        for file in pictures:
            # print(str(datetime.datetime.now()), file)
            unix_epoch = file[0:10]
            temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
            if temp_date_object > start_date_object and temp_date_object < end_date_object:
                picture_count+=1
                shutil.copy("Output/Pictures/Camera"+camera_selection.get()+"/"+file, "temp")


        # Give duration options, delete temp files to achieve selected duration
        picture_count = chooseDuration(picture_count)


        # Render if we have pictures
        if picture_count >= 1:
            print(str(datetime.datetime.now()), "Rendering using ffmpeg")

            global renderingThread

            if renderingThread.is_alive():
                print(str(datetime.datetime.now()), "Rendering thread alive, won't start a new one")
            else:   
                # Start Rendering in the background
                renderingThread = threading.Thread(target=runRenderingScript)
                renderingThread.setDaemon(True)
                renderingThread.start()

            # Call progress bar 
            progressBar(picture_count)

        elif picture_count == -1:
            print(str(datetime.datetime.now()), "Aborting Render")
            messagebox.showerror("Error", "Aborting Render")
            return
        else:
            print(str(datetime.datetime.now()), "Not enough pictures for playback")
            messagebox.showerror("Error", "Not enough pictures for rendering")
            return

        # Remove temp directory
        if os.path.isdir("temp"):
            shutil.rmtree("temp")


        # Check if video has been rendered succesfully
        checkRender(picture_count)

    else:
        print(str(datetime.datetime.now()), "No Camera Selected")
        messagebox.showerror("Error", "No camera selected for rendering")
        return

# Runs timelapse.sh script as a separate thread so that tkinter can properly update the GUI
def runTimelapseScript():



    # Run timelapse script here
    timelapse_process = subprocess.run(["./timelapse.sh"], shell=False)
    if timelapse_process.returncode == 1:
        print(str(datetime.datetime.now()), "An error has occured in timelapse.sh")
        messagebox.showerror("Error", "An error has occured in timelapse.sh")


    return



    global camera_ips
    global camera_usernames
    global camera_passwords
    global camera_interval
    global camera_start_hour
    global camera_end_hour


    root.title("Timelapse is running")

    print(str(datetime.datetime.now()), "runTimelapseScript()")
    print(str(datetime.datetime.now()), "camera_ips: ", camera_ips)
    print(str(datetime.datetime.now()), "camera_usernames: ", camera_usernames)
    print(str(datetime.datetime.now()), "camera_passwords: ", camera_passwords)
    print(str(datetime.datetime.now()), "camera_interval: ", camera_interval)
    print(str(datetime.datetime.now()), "camera_start_hour: ", camera_start_hour)
    print(str(datetime.datetime.now()), "camera_end_hour: ", camera_end_hour)


    # For some reason the timelapse settings are not decrypted here

    try:
        camera_interval = trivial_decrypt(camera_interval)
    except Exception as e:
        print(str(datetime.datetime.now()), "Cannot decrypt camera_interval")
        messagebox.showerror("Error", "Cannot decrypt camera_interval")
        return


    # Get current thread so we can see if its supposed to stop
    t = threading.current_thread()

    # timelapse.sh script takes one picture and quits
    while True:
        start_time = timeit.default_timer()
        # Check if we should still run
        if not getattr(t, "do_run", True):
            print(str(datetime.datetime.now()), "Stopped by stopTimelapse()")
            break
        # Take a picture and save it in Output/Pictures
        result = subprocess.run(["./timelapse.sh"], shell=False)

        if result.returncode == 1:
            print(str(datetime.datetime.now()), "An error has occured in timelapse.sh")
            messagebox.showerror("Error", "An error has occured in timelapse.sh")
            return
        # code you want to evaluate
        elapsed = timeit.default_timer() - start_time

        # Sleep for required seconds (takes into account the time to complete one loop iteration)
        time.sleep(int(camera_interval) - int(elapsed))

# Main Functionality of app is here
def startTimelapse():


    global camera_ips
    global camera_usernames
    global camera_passwords
    global camera_interval
    global camera_start_hour
    global camera_end_hour
    global camera_store_last

    # Remove .stop if it exists
    file_exists = os.path.exists(".stop")
    if file_exists:
        os.remove(".stop")

    # Updates the global list variables
        # Load settings in internal data structures
    quit = readTimelapseSettings()

    # # Quit if we can't read config files
    if quit == 1:
        # sys.exit()
        messagebox.showerror("Error", "Please configure the program via the menu")

    # Quit if timelapse settings are incorrect
    if quit == 1:
        return

    quit = testRTSPCameras()

    # Quit if RTSP is not reachable
    if quit == 1:
        return


    print("startTimelapse()")
    print("camera_interval: ", camera_interval)

    

    # timelapse_settings.txt is written here
    writeTimelapseSettings()

    print(str(datetime.datetime.now()), cameras)


    # Create any missing folder structures
    quit = checkDirectories()

    # Quit if folder structure has been modified since starting the program
    if quit == 1:
        return


    command = ['pgrep', 'timelapse.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # So we don't expode the server
    # Stop if rendering script is running already for some reason
    if result.stdout:
        print(str(datetime.datetime.now()), "timelapse.sh script is already running, exiting")
        messagebox.showerror("Error", "timelapse.sh script is already running")
        return
    else:
        print(str(datetime.datetime.now()), "timelapse.sh script not running, continuing")


    # Old way of doing things
    global timelapseThread

    if timelapseThread.is_alive():
        print(str(datetime.datetime.now()), "Timelapse thread alive, won't start a new one")
        messagebox.showerror("Error", "timelapse.sh script is already running")
        return
    else:   
        # Start Rendering in the background
        timelapseThread = threading.Thread(target=runTimelapseScript)
        timelapseThread.setDaemon(True)
        timelapseThread.start()

        if timelapseThread.is_alive():
            messagebox.showinfo("Success", "Timelapse is running")
        else:
            messagebox.showerror("Error", "Timelapse has not started")

    return

# Stops the timelapse process
def stopTimelapse():

    command = ['pgrep', 'timelapse.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # So we don't expode the server
    # Stop if rendering script is running already for some reason
    if result.stdout:
        print(str(datetime.datetime.now()), "timelapse.sh script is already running, creating .stop and killing")
        # messagebox.showinfo("Success", "Stopping timelapse script, please wait a few seconds")
        f = open(".stop", "w")
        f.close()
        kill_process("timelapse.sh")
        return
        
    else:
        print(str(datetime.datetime.now()), "timelapse.sh script not running")
        messagebox.showerror("Error", "timelapse.sh script not running")
        return



    # Old way of doing things
    if timelapseThread.is_alive():
        print(str(datetime.datetime.now()), "Timelapse Thread is running")
        # Signal playback thread to stop
        timelapseThread.do_run = False
        root.title("Timelapse not running")
        messagebox.showinfo("Stopped", "Timelapse has stopped")
    else:
         messagebox.showerror("Error", "No timelapse running")

    return

# This runs as a separate thread so that tkinter can properly update the GUI
def timelapsePlayback():
    
    global label
    global camera_selection
    global current_playback_image
    global p2 # Main menu progress bar
    global root # Main menu tkinter thingy
    global current_picture_label
    global total_pictures_label
    global playback_speed


    string_playback_speed = playback_speed.get()

    print(str(datetime.datetime.now()), "Selected playback speed ", string_playback_speed)

    playback_skip = 1

    if string_playback_speed == "1x":
        playback_skip = 1
    elif string_playback_speed == "2x":
        playback_skip = 2
    elif string_playback_speed == "4x":
        playback_skip = 4
    elif string_playback_speed == "8x":
        playback_skip = 8
    elif string_playback_speed == "16x":
        playback_skip = 16
    elif string_playback_speed == "32x":
        playback_skip = 32
    elif string_playback_speed == "64x":
        playback_skip = 64




    # Get current thread so we can see if its supposed to stop
    t = threading.current_thread()

    if not camera_selection.get():
        print(str(datetime.datetime.now()), "No camera selected")
        messagebox.showerror("Error", "No camera selected")
        return

    quit = checkDirectories()

    # Quit if folder structure has been modified since starting the program
    if quit == 1:
        return



    camera_directory = 'Output/Pictures/Camera' + camera_selection.get()
    

    pictures = os.listdir(path=camera_directory)
    alphabetic_pictures = sorted(pictures)

    if not pictures:
        messagebox.showerror("Error", "No Pictures to show")
        return



    # Check if dates were given correctly
    if start_date_cal.get_date() > end_date_cal.get_date():
        messagebox.showerror("Error", "Start date must be before end date")
        return


    # Convert them to strings because of bad life choices
    start_date = str(start_date_cal.get_date().day)+"/"+str(start_date_cal.get_date().month)+"/"+str(start_date_cal.get_date().year) # e.g. start_date "15/10/2021"
    end_date = str(end_date_cal.get_date().day)+"/"+str(end_date_cal.get_date().month)+"/"+str(end_date_cal.get_date().year) # e.g. start_date "17/10/2021"

    # Convert user input to date object and catch potential exceptions (Not gonna happen but I had this coded up so ohh well)
    try:
        start_date_object = datetime.datetime.strptime(start_date,"%d/%m/%Y")
        end_date_object = datetime.datetime.strptime(end_date+" 23:59:59","%d/%m/%Y %H:%M:%S")
    except Exception as e:
        print(str(datetime.datetime.now()), "Wrong date format")
        messagebox.showerror("Error", "Wrong date format")
        return

     
    print(str(datetime.datetime.now()), "timelapsePlayback()")
    print(str(datetime.datetime.now()), start_date_object)
    print(str(datetime.datetime.now()), end_date_object)

    playback_flag = 0
    progress = 0
    playback_speed_counter = 0 # For playback speed


    for file in alphabetic_pictures:
        
        # Skip anything that is not a jpeg
        if file[-5:] != ".jpeg":
            continue

        if playback_skip != 1:
            if playback_speed_counter % playback_skip != 0:
                playback_speed_counter+=1
                continue


        print(str(datetime.datetime.now()), file)

        unix_epoch = file[0:10]
        temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
        current_playback_image = alphabetic_pictures.index(file)
        progress = int(current_playback_image/(len(alphabetic_pictures))*100)

        # Check if we should still run (quits if this is true)
        if not getattr(t, "do_run", True):
            # Load first picture when stopping (more intuitive)
            temp_image = ImageTk.PhotoImage(Image.open(camera_directory + "/" + alphabetic_pictures[0]).resize((1000,700), Image.ANTIALIAS))
            label.configure(image = temp_image)
            label.image = temp_image
            p2["value"] = 0
            root.update() 
            break

        if not getattr(t, "do_pause", True):
            print(str(datetime.datetime.now()), "Stopped at picture with index ", current_playback_image)
            break

        
        # Check if playback dates are within user selected dates
        if temp_date_object > start_date_object and temp_date_object < end_date_object:
            # Keep loading the next image if not supposed to stop
            temp_image = ImageTk.PhotoImage(Image.open(camera_directory + "/" + file).resize((1000,700), Image.ANTIALIAS))
            label.configure(image = temp_image)
            label.image = temp_image
            playback_flag = 1
            # time.sleep(1)

        p2["value"] = progress
        root.update() 
        playback_speed_counter+=1


    # If no pictures are played back tell user
    if playback_flag == 0:
        messagebox.showerror("Error", "No pictures captured for selected dates")
        p2["value"] = 0
        root.update() 
        return


    # Reset Playback counters and progressbars
    for file in alphabetic_pictures:
        unix_epoch = file[0:10]
        temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
        # Check if playback dates are within user selected dates
        if temp_date_object > start_date_object and temp_date_object < end_date_object:
            # Keep loading the next image if not supposed to stop
            temp_image = ImageTk.PhotoImage(Image.open(camera_directory + "/" + file).resize((1000,700), Image.ANTIALIAS))
            label.configure(image = temp_image)
            label.image = temp_image
            p2["value"] = 0
            root.update() 
            break

# Starts timelapse playback thread in the background
def startPlayback():
    print(str(datetime.datetime.now()), "Start Date: ", start_date_cal.get_date())
    print(str(datetime.datetime.now()), "End Date: ", end_date_cal.get_date())

    global playbackThread

    if playbackThread.is_alive():
        print(str(datetime.datetime.now()), "Playback Thread is running")
    else:
        # Start Rendering in the background
        playbackThread = threading.Thread(target=timelapsePlayback)
        playbackThread.setDaemon(True)
        playbackThread.start()

    return

#  Stops the playback process
def stopPlayback():

    if playbackThread.is_alive():
        print(str(datetime.datetime.now()), "Playback Thread is running")
        # Signal playback thread to stop
        playbackThread.do_run = False
    
    return

# Pauses the playback process
def pausePlayback():

    if playbackThread.is_alive():
        print(str(datetime.datetime.now()), "Playback Thread is running")
        # Signal playback thread to pause
        playbackThread.do_pause =False

    return

# Date Choosing
def example1():
    def print_sel():
        print(str(datetime.datetime.now()), cal.selection_get())
        top.destroy()

    top = tk.Toplevel(root)

    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=2021, month=2, day=5)
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="ok", command=print_sel).pack()
    
# Date choosing
def example2():
    top = tk.Toplevel(root)

    ttk.Label(top, text='Choose date').pack(padx=10, pady=10)

    cal = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
    cal.pack(padx=10, pady=10)

# Chad retarted function, sigma male grindset
def donothing():
    return

# Kills rendering thread
def abortRender():

    # global rendering_process
    # rendering_process.kill()
    
    kill_process("render.sh")

    return

# Video rendering progress bar
def progressBar(picture_count):

    def ffmpeg_progress(picture_count):

        command = ['pgrep', 'render.sh']
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        ffmpeg_frames_rendered = 0

        # While render.sh script is running check the progress %
        while result.stdout:
            
            print(str(datetime.datetime.now()), "render.sh is running!")

            # Read ffmpeg output and deduce whether succeess or not

            # Update Progress bar and percentage text
            for line in reversed(list(open("output.txt"))):
                if line.rstrip().startswith("frame="):
                    
                    ffmpeg_frames_rendered = line.rstrip()[6::]

                    progress = int(ffmpeg_frames_rendered)/picture_count*100

                    print(str(datetime.datetime.now()), "ProgressBar progress: ", progress)

                    textProgress.set(str(int(progress))+"% Done")

                    p1["value"] = progress
                    popup.update()    
                    break

            # # Update ETA text
            for line in reversed(list(open("output.txt"))):
                if line.rstrip().startswith("fps="):
                    
                    ffmpeg_fps=line.rstrip()[4::]

                    print(str(datetime.datetime.now()), ffmpeg_fps)

                    # ffmpeg_fps -----> 1 second
                    # picture count ===> x seconds

                    if float(ffmpeg_fps) != 0.0:
                        eta = (picture_count-int(ffmpeg_frames_rendered))/float(ffmpeg_fps)
                    else:
                        eta = 0.0
                    
                    print(str(datetime.datetime.now()), "ProgressBar ETA: ", eta)
                    # textProgress.set(str(int(progress))+"%")
                    textETA.set("ETA: "+str(int(eta))+" seconds")   
                    break

            time.sleep(0.1)   
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # Wait such that render.sh actually starts
    time.sleep(1)

    textProgress = tk.StringVar()
    textProgress.set("0%")

    textETA = tk.StringVar()
    textETA.set("")

    #start progress bar
    popup = tk.Toplevel()
    popup.title("Rendering...")
    tk.Label(popup, text="Video is being rendered").grid(row=0,column=0)
    tk.Label(popup, textvariable=textProgress).grid(row=4,column=0)
    tk.Label(popup, textvariable=textETA).grid(row=5,column=0)
    tk.Button(popup,text= "Abort", command=abortRender).grid(row=6,column=0)

    p1 = Progressbar(popup, length=200, cursor='spider', mode="determinate", orient=tk.HORIZONTAL)
    p1.grid(row=2,column=0)
    ffmpeg_progress(picture_count)
    popup.destroy()

    return 0

# Separate function so we can run it on its own thread
def runRenderingScript():

    rendering_process = subprocess.run(["./render.sh"], shell=False)
    if rendering_process.returncode == 1:
        print(str(datetime.datetime.now()), "An error has occured in render.sh")
        messagebox.showerror("Error", "An error has occured in render.sh")

# Check if directories exist and consruct them
def createDirectories():

    global camera_selection

    # Check if Output directory exists
    if not os.path.exists("Output"):
        print(str(datetime.datetime.now()), "No output directory")
        os.mkdir("Output")


    

    # Check if Picture directory exists
    if not os.path.exists("Output/Pictures"):
        print(str(datetime.datetime.now()), "No Pictures directory")
        os.mkdir("Output/Pictures")

    # Check if Video directory exists
    if not os.path.exists("Output/Videos"):
        print(str(datetime.datetime.now()), "No Videos directory")
        os.mkdir("Output/Videos")


    print(str(datetime.datetime.now()), "There exist ", len(cameras), " cameras")

    # Check if Camera directories exist
    if camera_selection:

        for i in range(len(cameras)):
            camera_folder = os.path.exists("Output/Pictures/Camera"+str(i))

            # print(str(datetime.datetime.now()), "Output/Pictures/Camera"+str(i), " ", camera_folder)

            if not camera_folder:
                print(str(datetime.datetime.now()), "No camera " + str(i) + " directory")
                os.mkdir("Output/Pictures/Camera"+str(i))




    # Make sure temp dir is removed
    if os.path.isdir("temp"):
        shutil.rmtree("temp")

# Checks if any missing directories exist and informs user
def checkDirectories():

    global camera_selection

    # Check if Output directory exists
    if not os.path.exists("Output"):
        messagebox.showerror("Error", "No output directory, restart program")
        return 1


    # Check if Picture directory exists
    if not os.path.exists("Output/Pictures"):
        messagebox.showerror("Error", "No Pictures directory, restart program")
        return 1

    # Check if Video directory exists
    if not os.path.exists("Output/Videos"):
        messagebox.showerror("Error", "No Videos directory, restart program")
        return 1


    # Check if Camera directories exist
    if camera_selection:

        for i in range(len(cameras)):
            camera_folder = os.path.exists("Output/Pictures/Camera"+str(i))

            # print(str(datetime.datetime.now()), str(datetime.datetime.now()), "Output/Pictures/Camera"+str(i), " ", camera_folder)

            if not camera_folder:
                messagebox.showerror("Error", "No camera " + str(i) + " directory, restart program")
                return 1
    
    return 0

# Password protected timelapse settings
def enterPassword():
    def close_win():
        password_popup.destroy()


    def checkPassword():
        user_password = password.get()
        if user_password == settings_password:
            close_win()
            timelapseSettings()
        else:
            messagebox.showerror("Error", "Wrong password")



    

    password_popup = tk.Toplevel()
    password_popup.title("Enter Password")
    password_popup.geometry("400x200")

    password =tk.StringVar(password_popup)

    # Create Entry Widget for password
    password = Entry(password_popup, textvariable = password, show="*",width=40)
    password.pack(pady=5)

    # Create a button to check the password
    Button(password_popup, text="Ok", font=('Helvetica bold',
    10),command=checkPassword).pack(pady=10)

    # Create a button to close the window
    Button(password_popup, text="Cancel", font=('Helvetica bold',
    10),command=close_win).pack(pady=10)



    return

# Constantly checks if the timelapse script is running
def timelapseStatusThread():


    # previous = 0

    while True:

        command = ['pgrep', 'timelapse.sh']
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        # So we don't expode the server
        # Stop if rendering script is running already for some reason
        if result.stdout:
            print(str(datetime.datetime.now()), "timelapse.sh script is already running")
            root.title("Timelapse is running")

            # if previous == 1:
            #     messagebox.showinfo("Notification", "Timelapse is running")
            # previous = 0
            
        else:
            print(str(datetime.datetime.now()), "timelapse.sh script not running")
            root.title("Timelapse is not running")

            # if previous == 0:
            #     messagebox.showinfo("Notification", "Timelapse is notrunning")
            # previous = 1
            

        sleep(1)

# Returns average size of pictures of a given camera in bytes
def getAveragePictureSize(camera_selection):


    camera_directory = 'Output/Pictures/Camera' + str(camera_selection)
            

    pictures = os.listdir(path=camera_directory)
    alphabetic_pictures = sorted(pictures)

    total_size = 0

    for picture in alphabetic_pictures:
        total_size += os.path.getsize(camera_directory+"/"+picture)


    average_size = total_size/len(alphabetic_pictures)

    print(str(datetime.datetime.now()), "Average Picture size for camera"+str(camera_selection) +" is "+str(average_size))


    return

# Contantly checks how many pictures are stored and deletes old ones
def deletePicturesThread():

    # User should choose to store the last N months and the code should do the rest
    

    while True:

        
        # print("Interval ", camera_interval)
        # print("Store last", camera_store_last, " months")

        presentDate = datetime.datetime.now()
        unix_timestamp = datetime.datetime.timestamp(presentDate)
        # print(int(unix_timestamp))

        unix_today = int(unix_timestamp)
        seconds_in_last_N_months = 2629743*int(camera_store_last)


        # Check if directories have been modified
        quit = checkDirectories()
        if quit:
            return
        

        for i in cameras:
            camera_directory = 'Output/Pictures/Camera' + str(i)
            

            pictures = os.listdir(path=camera_directory)
            alphabetic_pictures = sorted(pictures)

            if not alphabetic_pictures:
                print(str(datetime.datetime.now()), "No pictures recorded by camera"+str(i))
                continue
            else:
                print(str(datetime.datetime.now()), len(pictures), " pictures recorded by camera"+str(i) )


            # getAveragePictureSize(i)

            for file in alphabetic_pictures:
                file_unix_epoch = file[0:10]

                # File is older than X months
                if int(file_unix_epoch) < (unix_today-seconds_in_last_N_months):
                    os.remove(camera_directory+"/"+file)


        sleep(int(camera_interval)*2)


    return

# Checks if pictures are being captured
def timelapseErrorThread():

    latest_picture_timestamps = []

    for i in cameras:
        latest_picture_timestamps.append(0)


    while True:

        command = ['pgrep', 'timelapse.sh']
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        # If timelapse script is running and directories exist check if actual new pictures are being captured
        if (checkDirectories() == 0) and result.stdout:

                for i in cameras:
                    camera_directory = 'Output/Pictures/Camera' + str(i)
                    pictures = os.listdir(path=camera_directory)
                    alphabetic_pictures = sorted(pictures)

                    # Pictures have not been taken ()
                    # Check camera start and end hours

                    now = datetime.datetime.now()
                    current_camera_hour = now.strftime("%H%M")
                    print(str(datetime.datetime.now())," Current Time =", current_camera_hour)


                    if (alphabetic_pictures[-1] == latest_picture_timestamps[i]) and (latest_picture_timestamps[i] != 0) and (int(current_camera_hour) <= int(camera_end_hour)) and (int(current_camera_hour) >= int(camera_start_hour)):
                        messagebox.showerror("Error","Timelape pictures are not being captured from camera"+str(i))
                        print(str(datetime.datetime.now()),"Timelape pictures are not being captured from camera"+str(i))
                        return
                    else:
                        latest_picture_timestamps[i] = alphabetic_pictures[-1]


                # print(latest_picture_timestamps)


        sleep(int(camera_interval)*2)



def writeRenderScript():

    script = r"""#!/bin/bash
LOG_FILE="output.txt"
FILENAME="out"
RENDER_SETTINGS_FILE="render_settings.txt"
START_DATE=$(sed '1q;d' $RENDER_SETTINGS_FILE)
END_DATE=$(sed '2q;d' $RENDER_SETTINGS_FILE)
FRAMERATE=$(sed '3q;d' $RENDER_SETTINGS_FILE)
CAMERA=$(sed '4q;d' $RENDER_SETTINGS_FILE)
FILENAME="camera"$CAMERA--$START_DATE--$END_DATE
ffmpeg -y -progress output.txt -framerate $FRAMERATE -pattern_type glob -i "temp/*.jpeg" -c:v libx264 -r $FRAMERATE -pix_fmt yuv420p "Output/Videos"/$FILENAME.mp4 #1> $LOG_FILE 2>&1"""


    render_script = open("render.sh", "w")
    render_script.write(script)
    render_script.close()
    os.chmod("render.sh",0o777)
    return


def writeTimelapseScript():

    script=r"""#!/bin/bash
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
#ffmpeg -ss 2 -rtsp_transport tcp -i rtsp://$USERNAME:$PASSWORD@$IP//h264Preview_01_main -y -f image2 -qscale 0 -frames 1  $DIRECTORY/$TODAY.jpeg"""

    timelapse_script = open("timelapse.sh", "w")
    timelapse_script.write(script)
    timelapse_script.close()
    os.chmod("timelapse.sh",0o777)
    return

# Collects various program stats for user feedback
def getStats():
    return


# Actual main function
if __name__ == "__main__":

    # log_file = open("debug.log", "a")
    # log_file.write(str(datetime.datetime.now()) + " " + "main()" +"\n")


    # Write sripts to disk since we will use them later
    writeRenderScript()
    writeTimelapseScript()


    # Load settings in internal data structures
    quit = readTimelapseSettings()

    # # Quit if we can't read config files
    if quit == 1:
        # sys.exit()
        messagebox.showerror("Error", "Please configure the program via the menu")


    # Remove .stop if it exists
    file_exists = os.path.exists(".stop")
    if file_exists:
        os.remove(".stop")



    # Create canvas
    canvas = tk.Canvas(root, height=900, width=1035)

    # Attach canvas
    canvas.pack()


    # pausePlayback = tk.Button(root,text="Pause Playback  ", padx=10, pady=5, command=pausePlayback)
    # pausePlayback.place(x=20, y=750)
    # # pausePlayback.pack()


    stopPlayback = tk.Button(root,text= "Stop Playback", padx=12, pady=5, command=stopPlayback)
    stopPlayback.place(x=20, y=760)
    # stopTimelapse.pack()

    startPlayback = tk.Button(root,text= "Start Playback", padx=12, pady=5, command=startPlayback)
    startPlayback.place(x=220, y=760)
    # playTimelapse.pack()


    renderVideo = tk.Button(root,text="Render Video", padx=12, pady=5, command=renderVideo)
    renderVideo.place(x=820, y=760)
    # renderVideo.pack()

    # Labels for clarity
    tk.Label(root, text="Camera").place(x=20, y=820)
    tk.Label(root, text="Start Date").place(x=820, y=800)
    tk.Label(root, text="End Date").place(x=820, y=850)
    tk.Label(root, text="Playbck Speed").place(x=220, y=820)

    # Playback Speed
    playback_speed = StringVar(root)
    playback_speed.set("1x") # default value

    select_playback_speed = OptionMenu(root, playback_speed, "1x", "2x", "4x", "8x", "16x", "32x", "64x")
    select_playback_speed.place(x=220, y=850)

    # Picking Dates
    # Get current date
    now = datetime.datetime.now()

    start_date_cal = DateEntry(root, width=12, year=now.year, month=now.month, day=now.day, 
    background='darkblue', foreground='white', borderwidth=2)
    start_date_cal.place(x=820, y=820)

    end_date_cal = DateEntry(root, width=12, year=now.year, month=now.month, day=now.day, 
    background='darkblue', foreground='white', borderwidth=2)
    end_date_cal.place(x=820, y=870)

    p2 = Progressbar(root, length=1000, cursor='spider', mode="determinate", orient=tk.HORIZONTAL)
    p2.place(x=20, y=730)


    camera_selection = tk.StringVar(root)

    # To avoid crash
    if len(cameras) != 0:
        camera_selection.set(cameras[0])
        camera_option = tk.OptionMenu(root, camera_selection, *cameras)
        camera_option.config(width=5, font=('Helvetica', 12))
        camera_option.place(x=20, y = 850)

    
    # Construct nessasary folder structures
    createDirectories()



    # Start timelapse status thread
    if statusThread.is_alive():
        print(str(datetime.datetime.now()), "Status thread alive, won't start a new one")
    else:   
        # Start Rendering in the background
        statusThread = threading.Thread(target=timelapseStatusThread)
        statusThread.setDaemon(True)
        statusThread.start()



    # Start delete thread
    if deleteThread.is_alive():
        print(str(datetime.datetime.now()), "Delete thread alive, won't start a new one")
    else:   
        # Start Rendering in the background
        deleteThread = threading.Thread(target=deletePicturesThread)
        deleteThread.setDaemon(True)
        deleteThread.start()


    # Start error checking thread thread
    if errorCheckThread.is_alive():
        print(str(datetime.datetime.now()), "Error check thread alive, won't start a new one")
    else:   
        # Start Rendering in the background
        errorCheckThread = threading.Thread(target=timelapseErrorThread)
        errorCheckThread.setDaemon(True)
        errorCheckThread.start()


    # Menu Items
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=donothing)
    filemenu.add_command(label="Open", command=donothing)
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_command(label="Save as...", command=donothing)
    filemenu.add_command(label="Close", command=donothing)
    filemenu.add_separator()

    filemenu.add_separator()

    filemenu.add_command(label="Exit", command=root.quit)

    # menubar.add_cascade(label="File", menu=filemenu)


    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo", command=donothing)
    editmenu.add_separator()
    editmenu.add_command(label="Cut", command=donothing)
    editmenu.add_command(label="Copy", command=donothing)
    editmenu.add_command(label="Paste", command=donothing)
    editmenu.add_command(label="Delete", command=donothing)
    editmenu.add_command(label="Select All", command=donothing)



    # Settings Menu
    settingsmenu = Menu(menubar, tearoff=0)
    # menubar.add_cascade(label="Settings", menu=settingsmenu)


    # Timelapse Menu
    timelapsemenu = Menu(menubar, tearoff=0)
    timelapsemenu.add_command(label="Start", command=startTimelapse)
    timelapsemenu.add_command(label="Stop", command=stopTimelapse)
    # timelapsemenu.add_command(label="Stitching", command=donothing)
    timelapsemenu.add_command(label="Settings", command=enterPassword)
    timelapsemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="Timelapse", menu=timelapsemenu)

    # menubar.add_cascade(label="Edit", menu=editmenu)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)


    # Load first image on canvas
    # pictures = os.listdir(path='Output/Pictures')
    # alphabetic_pictures = sorted(pictures)


    # Convert them to strings because of bad life choices
    start_date = str(start_date_cal.get_date().day)+"/"+str(start_date_cal.get_date().month)+"/"+str(start_date_cal.get_date().year) # e.g. start_date "15/10/2021"
    end_date = str(end_date_cal.get_date().day)+"/"+str(end_date_cal.get_date().month)+"/"+str(end_date_cal.get_date().year) # e.g. start_date "17/10/2021"


    valid_dates = False

    # Convert user input to date object and catch potential exceptions (Not gonna happen but I had this coded up so ohh well)
    try:
        start_date_object = datetime.datetime.strptime(start_date,"%d/%m/%Y")
        end_date_object = datetime.datetime.strptime(end_date+" 23:59:59","%d/%m/%Y %H:%M:%S")
        valid_dates = True

    except Exception as e:
        print(str(datetime.datetime.now()), str(datetime.datetime.now()), "Wrong date format")
        messagebox.showerror("Error", "Wrong date format")
        

    label = tk.Label(root)
    label.place(x=20, y=20)


    # Run GUI
    root.mainloop()


    # log_file.close()
