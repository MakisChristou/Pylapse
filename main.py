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

root = tk.Tk()
root.title("Timelapse not running")
root.resizable(width=False, height=False)

# Bonus ability because of Agathangelou requirements
def renderVideo():
    command = ['pgrep', 'render.sh']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    # So we don't expode the server
    # Stop if rendering script is running already for some reason
    if result.stdout:
        print("render.sh script is already running, exiting")
        messagebox.showerror("Error", "render.sh script is already running")
        return
    else:
        print("render.sh script not running, continuing")


    print(type(start_date_cal.get_date()))

    print(str(start_date_cal.get_date().year))


    if start_date_cal.get_date() > end_date_cal.get_date():
        messagebox.showerror("Error", "Start date must be before end date")
        return


    # Convert them to strings because of bad life choices
    start_date = str(start_date_cal.get_date().day)+"/"+str(start_date_cal.get_date().month)+"/"+str(start_date_cal.get_date().year) # e.g. start_date "15/10/2021"
    end_date = str(end_date_cal.get_date().day)+"/"+str(end_date_cal.get_date().month)+"/"+str(end_date_cal.get_date().year) # e.g. start_date "17/10/2021"
    framerate = "30"



    # Check if variables are empty
    if not start_date or not end_date or not framerate:
        print("At least one variable is empty")
        messagebox.showerror("Error", "At least one variable is empty")
        return

    # Convert user input to date object and catch potential exceptions
    try:
        start_date_object = datetime.datetime.strptime(start_date,"%d/%m/%Y")
        end_date_object = datetime.datetime.strptime(end_date+" 23:59:59","%d/%m/%Y %H:%M:%S")
    except Exception as e:
        print("Wrong date format")
        messagebox.showerror("Error", "Wrong date format")
        return

    # Check if framerate is integer
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


    pictures = os.listdir(path='Output/Pictures')

    picture_count = 0

    # Make sure temp dir is empty
    if os.path.isdir("temp"):
        shutil.rmtree("temp")

    os.mkdir("temp")

    print("Copying files to temp dir")

    for file in pictures:
        unix_epoch = file[0:10]
        temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
        if temp_date_object > start_date_object and temp_date_object < end_date_object:
            picture_count+=1
            shutil.copy("Output/Pictures/"+file, "temp")


    print("Timelapse will be composed of ", picture_count, " pictures")

    # Render if we have pictures
    if picture_count >= 1:
        print("Rendering using ffmpeg")
        # Start Rendering
        print(subprocess.run(["./render.sh"], shell=False))
    else:
        print("Not enough pictures for playback")
        messagebox.showerror("Error", "Not enough pictures for rendering")
        return

    # Remove temp directory
    if os.path.isdir("temp"):
        shutil.rmtree("temp")


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
        exit
    else:
        print("timelapse.sh script not running, continuing")


    print(subprocess.run(["./timelapse.sh"], shell=False))


# Not working :/
def playTimelapse():
    print("Start Date: ", start_date_cal.get_date())
    print("End Date: ", end_date_cal.get_date())

    second_image = ImageTk.PhotoImage(Image.open("Output/Pictures/1634395354.jpeg").resize((1000,700), Image.ANTIALIAS))
    # image_on_canvas = canvas.create_image(20,20, anchor=NW, image=first_image) 
    
    print(image_on_canvas)

    canvas.itemconfig(image_on_canvas, image=second_image)

    # pictures = os.listdir(path='Output/Pictures')
    # for file in pictures:
    #     unix_epoch = file[0:10]
    #     temp_date_object = datetime.datetime.fromtimestamp(int(unix_epoch))
    #     print("Output/Pictures/"+file)
    #     new_image = ImageTk.PhotoImage(Image.open("Output/Pictures/"+file).resize((1000,700), Image.ANTIALIAS))
    #     canvas.itemconfig(image_on_canvas, image = new_image)
    #     time.sleep(2.4)



    return


def stopTimelapse():
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


# root = tk.Tk()
# s = ttk.Style(root)
# s.theme_use('clam')

# ttk.Button(root, text='Calendar', command=example1).pack(padx=10, pady=10)
# ttk.Button(root, text='DateEntry', command=example2).pack(padx=10, pady=10)

# root.mainloop()


# Create canvas
canvas = tk.Canvas(root, height=900, width=1035)

# Attach canvas
canvas.pack()


# Create three buttons
# openFiles = tk.Button(root,text="Open Files", padx=10, pady=5)
# openFiles.place(x=200, y=850)
# openFile.pack()

startTimelapse = tk.Button(root,text="Start Timelapse", padx=10, pady=5, command=startTimelapse)
# startTimelapse.place(x=175, y=100)
# startTimelapse.pack()


stopTimelapse = tk.Button(root,text="Stop Timelapse", padx=10, pady=5, command=stopTimelapse)
stopTimelapse.place(x=200, y=750)
# stopTimelapse.pack()

playTimelapse = tk.Button(root,text="Play Timelapse", padx=10, pady=5, command=playTimelapse)
playTimelapse.place(x=400, y=750)
# playTimelapse.pack()


renderVideo = tk.Button(root,text="Render Video", padx=10, pady=5, command=renderVideo)
renderVideo.place(x=600, y=750)
# renderVideo.pack()


# startDate = tk.Button(root, text="Start Date", padx=10, pady=5, command=example1)
# startDate.pack()

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
timelapsemenu.add_command(label="Start", command=donothing)
timelapsemenu.add_command(label="Stop", command=donothing)
timelapsemenu.add_command(label="Stitching", command=donothing)
menubar.add_cascade(label="Timelapse", menu=timelapsemenu)



menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)


# Showing Images
#Load an image in the script
# img= (Image.open("Output/Pictures/1634395228.jpeg"))

#Resize the Image using resize method
# resized_image= Image.open("Output/Pictures/1634395228.jpeg").resize((1000,700), Image.ANTIALIAS)

first_image= ImageTk.PhotoImage(Image.open("Output/Pictures/1634395228.jpeg").resize((1000,700), Image.ANTIALIAS))
image_on_canvas = canvas.create_image(20,20, anchor=NW, image=first_image) 

print(image_on_canvas)


# my_images = []
# my_images.append(PhotoImage(file = "Output/Pictures/1634395228.jpeg"))
# my_images.append(PhotoImage(file = "Output/Pictures/1634395242.jpeg"))
# my_images.append(PhotoImage(file = "Output/Pictures/1634395256.jpeg"))
# my_image_number = 1

# canvas.itemconfig(image_on_canvas, image = my_images[my_image_number])
  
# Run GUI
root.mainloop()