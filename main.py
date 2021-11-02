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


root = tk.Tk()
root.title("Timelapse not running")
root.resizable(width=False, height=False)

user_choice = ""
picture_count = 0
interval=10
playbackThread = threading.Thread()
renderingThread = threading.Thread()
timelapseThread = threading.Thread()


# Write timelapse settings to its relevant text file
def timelapseSettings():
    return

# Check if video has been rendered succesfully, notify User if error or not
def checkRender(picture_count):
    # Read ffmpeg output and deduce whether succeess or not
    for line in reversed(list(open("output.txt"))):
        if line.rstrip().startswith("frame="):
            
            ffmpeg_frames_rendered=line.rstrip()[6::]

            print(ffmpeg_frames_rendered)
            print(picture_count)

            if ffmpeg_frames_rendered == str(picture_count):
                messagebox.showinfo("Success", "Video has been succeesfully rendered")
            else:
                messagebox.showerror("Error", "Video has not rendered sucesfully")
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
    variable = StringVar(popup)
    variable.set(durations[0]) # default value

    w = OptionMenu(popup, variable, *durations)
    w.pack()

    button = Button(popup, text="OK", command=ok)
    button.pack()

    # Pause execution until user chooses duration
    root.wait_window(popup)


    keep_one_every = durations.index(int(user_choice))+1

    print("User choice is ", user_choice)
    print("Keeping one every ", keep_one_every, " pictures")
    print("Durations are ", durations)
    print("Timelapse will be composed of ", picture_count, " pictures")


    # Remove files from temporary directory to match user desired duration
    temp_pictures = os.listdir(path='temp')
    counter = 1
    for file in temp_pictures:
        
        file_path="temp/"+file

        if not ((counter % keep_one_every) == 0):
            os.remove(file_path)
            picture_count-=1
        
        counter+=1


    print("Timelapse will be composed of ", picture_count, " pictures")

    return picture_count

# Bonus ability because of Agathangelou requirements
def renderVideo():
    # Checks if render.sh script is running
    command = ['pgrep', 'render.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # Stop if rendering script is running already for some reason (So we don't expode the server)
    if result.stdout:
        print("render.sh script is already running, exiting")
        messagebox.showerror("Error", "render.sh script is already running")
        return
    else:
        print("render.sh script not running, continuing")


    # print(type(start_date_cal.get_date()))
    # print(str(start_date_cal.get_date().year))

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
        print("At least one variable is empty")
        messagebox.showerror("Error", "At least one variable is empty")
        return

    # Convert user input to date object and catch potential exceptions (Not gonna happen but I had this coded up so ohh well)
    try:
        start_date_object = datetime.datetime.strptime(start_date,"%d/%m/%Y")
        end_date_object = datetime.datetime.strptime(end_date+" 23:59:59","%d/%m/%Y %H:%M:%S")
    except Exception as e:
        print("Wrong date format")
        messagebox.showerror("Error", "Wrong date format")
        return

    # Check if framerate is integer (Not gonna happen but I had this coded up so ohh well)
    try:
        int(framerate)
    except Exception as e:
        print("Wrong framerate")
        messagebox.showerror("Error", "Wrong framerate")
        return


    # Write to file (for render.sh script)
    render_settings_file = open("render_settings.txt", "w")
    render_settings_file.write(start_date.replace("/", "-")+"\n")
    render_settings_file.write(end_date.replace("/", "-")+"\n")
    render_settings_file.write(framerate+"\n")
    render_settings_file.close()


    

    picture_count = 0

    # Make sure temp dir is empty
    if os.path.isdir("temp"):
        shutil.rmtree("temp")

    os.mkdir("temp")

    
    print("Copying files to temp dir")
    pictures = os.listdir(path='Output/Pictures')

    # Why do I have to do this? (bug)
    # pictures.remove(".jpeg")

    # Copy everyting to temp dir
    for file in pictures:
        # print(file)
        unix_epoch = file[0:10]
        temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
        if temp_date_object > start_date_object and temp_date_object < end_date_object:
            picture_count+=1
            shutil.copy("Output/Pictures/"+file, "temp")


    # Give duration options, delete temp files to achieve selected duration
    picture_count = chooseDuration(picture_count)


    # Render if we have pictures
    if picture_count >= 1:
        print("Rendering using ffmpeg")

        global renderingThread

        if renderingThread.is_alive():
            print("Renderinf thread alive, won't start a new one")
        else:   
            # Start Rendering in the background
            renderingThread = threading.Thread(target=runRenderingScript)
            renderingThread.setDaemon(True)
            renderingThread.start()

        # Call progress bar 
        progressBar(picture_count)

    else:
        print("Not enough pictures for playback")
        messagebox.showerror("Error", "Not enough pictures for rendering")
        return

    # Remove temp directory
    if os.path.isdir("temp"):
        shutil.rmtree("temp")


    # Check if video has been rendered succesfully
    checkRender(picture_count)

# Runs timelapse.sh script as a separate thread so that tkinter can properly update the GUI
def runTimelapseScript():

    root.title("Timelapse running")

    # Get current thread so we can see if its supposed to stop
    t = threading.current_thread()

    # timelapse.sh script takes one picture and quits
    while True:
        # Check if we should still run
        if not getattr(t, "do_run", True):
            print("Stopped by stopTimelapse()")
            break
        # Take a picture and save it in Output/Pictures
        print(subprocess.run(["./timelapse.sh"], shell=False))

        time.sleep(interval)

# Main Functionality of app is here
def startTimelapse():
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
        messagebox.showerror("Error", "timelapse.sh script is already running")
        return
    else:
        print("timelapse.sh script not running, continuing")


    global timelapseThread

    if timelapseThread.is_alive():
        print("Timelapse thread alive, won't start a new one")
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
    if timelapseThread.is_alive():
        print("Timelapse Thread is running")
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

    # Get current thread so we can see if its supposed to stop
    t = threading.current_thread()

    pictures = os.listdir(path='Output/Pictures')
    alphabetic_pictures = sorted(pictures)

    if not pictures:
        messagebox.showerror("Error", "No Pictures to show")
        return

    
    for file in alphabetic_pictures:
        print(file)

        # Check if we should still run
        if not getattr(t, "do_run", True):
            # Load first picture when stopping (more intuitive)
            temp_image = ImageTk.PhotoImage(Image.open("Output/Pictures/"+alphabetic_pictures[0]).resize((1000,700), Image.ANTIALIAS))
            label.configure(image = temp_image)
            label.image = temp_image
            break
        
        # Keep loading the next image if not supposed to stop
        temp_image = ImageTk.PhotoImage(Image.open("Output/Pictures/"+file).resize((1000,700), Image.ANTIALIAS))
        label.configure(image = temp_image)
        label.image = temp_image
        # time.sleep(1)

# Starts timelapse playback thread in the background
def startPlayback():
    print("Start Date: ", start_date_cal.get_date())
    print("End Date: ", end_date_cal.get_date())

    global playbackThread

    if playbackThread.is_alive():
        print("Playback Thread is running")
    else:
        # Start Rendering in the background
        playbackThread = threading.Thread(target=timelapsePlayback)
        playbackThread.setDaemon(True)
        playbackThread.start()

    return

#  Stops the playback process
def stopPlayback():

    if playbackThread.is_alive():
        print("Playback Thread is running")
        # Signal playback thread to stop
        playbackThread.do_run = False
    
    return

# Date Choosing
def example1():
    def print_sel():
        print(cal.selection_get())
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

# Video rendering progress bar
def progressBar(picture_count):

    def ffmpeg_progress(picture_count):

        command = ['pgrep', 'render.sh']
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

        ffmpeg_frames_rendered = 0

        # While render.sh script is running check the progress %
        while result.stdout:
            
            print("render.sh is running!")

            # Read ffmpeg output and deduce whether succeess or not

            # Update Progress bar and percentage text
            for line in reversed(list(open("output.txt"))):
                if line.rstrip().startswith("frame="):
                    
                    ffmpeg_frames_rendered = line.rstrip()[6::]

                    progress = int(ffmpeg_frames_rendered)/picture_count*100

                    print("ProgressBar progress: ", progress)

                    textProgress.set(str(int(progress))+"% Done")

                    p1["value"] = progress
                    popup.update()    
                    break

            # # Update ETA text
            for line in reversed(list(open("output.txt"))):
                if line.rstrip().startswith("fps="):
                    
                    ffmpeg_fps=line.rstrip()[4::]

                    print(ffmpeg_fps)

                    # ffmpeg_fps -----> 1 second
                    # picture count ===> x seconds

                    if float(ffmpeg_fps) != 0.0:
                        eta = (picture_count-int(ffmpeg_frames_rendered))/float(ffmpeg_fps)
                    else:
                        eta = 0.0
                    
                    print("ProgressBar ETA: ", eta)
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
    tk.Label(popup, text="Video is being rendered").grid(row=0,column=0)
    tk.Label(popup, textvariable=textProgress).grid(row=4,column=0)
    tk.Label(popup, textvariable=textETA).grid(row=5,column=0)

    p1 = Progressbar(popup, length=200, cursor='spider', mode="determinate", orient=tk.HORIZONTAL)
    p1.grid(row=2,column=0)
    ffmpeg_progress(picture_count)
    popup.destroy()

    return 0

# Separate function so we can run it on its own thread
def runRenderingScript():
    process = subprocess.run(["./render.sh"], shell=False)

    

# Actual main function
if __name__ == "__main__":

    # Create canvas
    canvas = tk.Canvas(root, height=900, width=1035)

    # Attach canvas
    canvas.pack()


    # startTimelapse = tk.Button(root,text="Start Timelapse", padx=10, pady=5, command=startTimelapse)
    # startTimelapse.place(x=200, y=850)
    # startTimelapse.pack()


    stopPlayback = tk.Button(root,text= "Stop Playback   ", padx=10, pady=5, command=stopPlayback)
    stopPlayback.place(x=200, y=750)
    # stopTimelapse.pack()

    startPlayback = tk.Button(root,text= "Start Playback   ", padx=10, pady=5, command=startPlayback)
    startPlayback.place(x=400, y=750)
    # playTimelapse.pack()


    renderVideo = tk.Button(root,text="Render Video", padx=10, pady=5, command=renderVideo)
    renderVideo.place(x=600, y=750)
    # renderVideo.pack()

    # Labels for clarity
    tk.Label(root, text="Start Date").place(x=400, y=820)
    tk.Label(root, text="End Date").place(x=600, y=820)

    # Picking Dates
    # Get current date
    now = datetime.datetime.now()

    start_date_cal = DateEntry(root, width=12, year=now.year, month=now.month, day=now.day, 
    background='darkblue', foreground='white', borderwidth=2)
    start_date_cal.place(x=400, y=850)

    end_date_cal = DateEntry(root, width=12, year=now.year, month=now.month, day=now.day, 
    background='darkblue', foreground='white', borderwidth=2)
    end_date_cal.place(x=600, y=850)


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
    menubar.add_cascade(label="File", menu=filemenu)
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
    menubar.add_cascade(label="Settings", menu=settingsmenu)


    # Timelapse Menu
    timelapsemenu = Menu(menubar, tearoff=0)
    timelapsemenu.add_command(label="Start", command=startTimelapse)
    timelapsemenu.add_command(label="Stop", command=stopTimelapse)
    timelapsemenu.add_command(label="Stitching", command=donothing)
    timelapsemenu.add_command(label="Settings", command=donothing)
    menubar.add_cascade(label="Timelapse", menu=timelapsemenu)



    menubar.add_cascade(label="Edit", menu=editmenu)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)


    # Check if images exist
    if not os.path.isdir("Output/Pictures"):
        messagebox.showerror("Error", "No Output Directory")
        os.mkdir("Output")
        os.chdir("Output")
        os.mkdir("Pictures")
        os.chdir('..')

    # Make sure temp dir is removed
    if os.path.isdir("temp"):
        shutil.rmtree("temp")


    pictures = os.listdir(path='Output/Pictures')
    alphabetic_pictures = sorted(pictures)

    if pictures:
        # Show first image on canvas
        first_image = ImageTk.PhotoImage(Image.open("Output/Pictures/" + alphabetic_pictures[0]).resize((1000,700), Image.ANTIALIAS))
        # image_on_canvas = canvas.create_image(20,20, anchor=NW, image=first_image)
    
        label = tk.Label(root, image=first_image)
        label.place(x=20, y=20)

    else:
        messagebox.showerror("Error", "No Pictures to show")
        label = tk.Label(root)
        label.place(x=20, y=20)

    # label = tk.Label(root, image=first_image)
    # label.place(x=20, y=20)


    # Run GUI
    root.mainloop()


    # if timelapseThread.is_alive():
    #     timelapseThread.join()