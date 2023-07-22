from bs4 import BeautifulSoup
import requests
from tkinter import *
import keyboard
import random
import os
os.chdir(os.path.realpath(os.path.dirname(__file__))) #so that the script can find prev.txt

avg_threshold=15 #CELSIUS | All temperatures will be in Celsius | The cutoff between warmer or lighter clothes
deviation_threshold=3 #No need to say the day gets hotter when the high is only 16.
wait_time=60 #IN SECONDS | How long for the the close button to appear
prob_of_reminder=1 #PERCENT | Regardless of prev or temperature, there is a [var] percent chance that the popup will be created.
url='accurate weather DAILY tab URL'

f=open("prev.txt","r+")
prev=f.read()

def determine_action(high,low):
    clothes=""
    note=""

    if (high+low)/2<=avg_threshold:
        clothes="warmer" #so the weather is colder
        if high>avg_threshold+deviation_threshold: #Ex temp: -100 to 30
            note="\nbut know that the day gets hotter"
    else:
        clothes="lighter"
        if low<avg_threshold-deviation_threshold: #Ex temp: -30 to 100
            note="\nbut know that the day starts/ends colder"

    return f"{clothes} clothes and shoes are needed{note}"

def create_popup(msg):
    root=Tk()
    root.attributes('-fullscreen', True)
    root.attributes("-topmost", True) #This popup will now be in focus for ALL the time

    msg_label=Label(root,text=msg,font=("Arial",50))
    msg_label.pack(pady=30)

    def unfreeze():
        keyboard.unhook_all() #unblocks all keyboard inputs | a bit redundant since -topmost already does the job.
        close_button=Button(root,text="Yes, I have switched or will switch to the appropriate clothing.",font=("Arial",20),command=root.destroy)
        close_button.pack(side=BOTTOM,pady=20)

        root.attributes("-topmost", False) #make alt+tab possible again

    root.update()

    for i in range(150):
        keyboard.block_key(i) #blocks all keyboard inputs except Ctrl+Alt+Delete

    root.after(wait_time*1000,unfreeze) #seconds to milliseconds

    root.mainloop()

response = requests.get(url,headers = {"User-Agent":"Mozilla/5.0"}) #to prevent access denied
soup = BeautifulSoup(response.content, 'html.parser')
information=[]

for raw_info in soup.find_all(class_='info')[:2]: #today and tomorrow
    temperature=raw_info.find(class_="temp").text
    date=raw_info.find(class_="module-header dow date").text+", "+raw_info.find(class_="module-header sub date").text

    high,low=map(lambda t: (int(t)- 32) * 5/9,temperature.replace("\n","").replace("°","").split("/"))
    #cleans up the raw temperature info ; converts each temperature into celsius

    information.append([(high,low),date,determine_action(high,low)])

#Comparing action messages
#if today and tommorow are the same, then don't do anything, since it is assumed that the user already has proper clothing from the previous alert.
#if not AND if it's not been alerted before (if action!=prev), then alert it.

if information[0][2]!=information[1][2] and information[1][2]!=prev:
    full_message=f"The temperature for tommorow, {information[1][1]}, is {round(information[1][0][0])} to {round(information[1][0][1])}, so\n{information[1][2]}."
    create_popup(full_message)
    f.write(information[1][2])
else:
    if random.random()<prob_of_reminder/100:
        full_message=f"The temperature for today, {information[0][1]}, is {round(information[0][0][0])} to {round(information[0][0][1])}, so\n{information[0][2]}."
        create_popup(full_message)

f.close()
