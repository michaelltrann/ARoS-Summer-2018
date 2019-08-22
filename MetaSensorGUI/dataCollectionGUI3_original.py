#!/usr/bin/env python3

from tkinter import Tk, Button, Label, messagebox
from tkinter.font import Font
import datetime
import multiprocessing
from subprocess import call,Popen,PIPE
import os


i = 1
j = 1
def start_sensor():
    global i
    global p
    global file
    global file2
    global file3
    if i == 1:
        logname = 'metaLog' + datetime.datetime.now().strftime('%m%d%y-%H%M')+ '.csv'
        file = open('/home/pi/Apps/MetaBase/MetaLogs/'+logname,'w')
        file2 = open('metaStatus.txt','w')
        file3 = open('metaStatus.txt','r')
        button1['text']='Connecting...'
        window.update()
        p=Popen('sudo npm start -- --config metabase-config.json --no-graph',stdin=PIPE,stdout=file2,universal_newlines=True,shell=True)
        window.after(15000)
        file2.flush()
        for line in file3:
            for word in line.split():
                if word == '[Enter]':
                    button1['text']='Running'
                    messagebox.showinfo('Notice','Connection Successful')
                    i = -1
            if i == -1: break
        if i == 1:
            file.close()
            file2.close()
            file3.close()
            os.remove(logname)
            messagebox.showinfo('Error','Failed to Connect, Press reset button on sensor and try again.')
            button1['text']='Start Data Collection'
#        p.communicate('xdotool key Return\n')
def system_timestamp():
    global j
    global i
    global file
    if i == -1:
        if j == 1:
            file.write(str(datetime.datetime.now()) + ',' + 'Start' + ',' + '1' + '\n')
            button2['text']='Stop'
            label2['text']='Status:\nActive'
            window.update()
        if j == -1:
            file.write(str(datetime.datetime.now()) + ',' + 'Stop' + ',' + '1' + '\n')
            response = messagebox.askyesno("Save Data", "Would you like to keep this data?")
            if response:
                file.write(str(datetime.datetime.now()) + ',' + 'Keep' + ',' + '1' + '\n')
            else:
                file.write(str(datetime.datetime.now()) + ',' + 'Discard' + ',' + '0' + '\n')
            button2['text']='Start'
            label2['text']='Status:\nIdle'
            window.update()
        j = j*-1

def stop_sensor():
    global i
    global p
    global file
    global file2
    global file3
    if i == -1:
        response = messagebox.askokcancel("Stop Data Collection", "Do you want to stop collecting data?")
        if response:
            button1['text']='Disconnecting...'
            window.update()
            p.communicate('xdotool key Return\n')
            window.after(10000)
            file2.flush()
            for line in file3:
                for word in line.split():
                    if word == 'Resetting':
                        file.close()
                        file2.close()
                        file3.close()
                        messagebox.showinfo('Notice','Disconnect Successful')
                        button1['text']='Start Data Collection'
                        window.update()
                        i = 1
                        break
                if i == 1:break
            if i == -1:
                messagebox.showinfo('Error','Disconnect Failed, Please try again.')
                button1['text'] = 'Running'
                window.update()


def exit_window():
    window.destroy()


if __name__ == '__main__':

    os.chdir('/home/pi/Apps/MetaBase')

    window = Tk()
    window.title("Sensor GUI")
    window.geometry('800x480')


    instruction = 'Instructions:\nSelect start to indicate activity\nof interest is occuring\nSelect stop to indicate activity\nof interest has concluded\nChoose to keep or \ndiscard the activity'

    myFont = Font(family = 'Helvetica',size=25,weight='bold')
    myFont2 = Font(family = 'Helvetica',size=15,weight='bold')
    button1 = Button(window, text='Run Data Collection',fg='green',font=myFont,command=start_sensor)
    button2 = Button(window, text='Start',fg='blue',font=myFont,command=system_timestamp)
    button3 = Button(window, text='Quit Data Collection',fg='red',font=myFont,command=stop_sensor)
    label1 = Label(window,text=instruction,font=myFont2,justify='left')
    label2 = Label(window,text='Status:\nIdle',font=myFont2,justify='left')


    label1.place(x=0,y=25)
    label2.place(x=0,y=250)
    button1.place(x=380,y=100)
    button3.place(x=380,y=200)
    button2.place(x=460,y=300)


    window.protocol("WM_DELETE_WINDOW", exit_window)
    window.mainloop()

