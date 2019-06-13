from __future__ import absolute_import
from __future__ import print_function

from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import os
import sys
import optparse
import subprocess
import random

import sqlite3
import csv

import matplotlib as mpl
mpl.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.pyplot as plt_veh

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    # from Tkinter import ttk
    import tkFileDialog
else:
    import tkinter as tk
    from tkinter import ttk
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as errorMessage
plt.switch_backend("Agg")

from matplotlib.colors import LogNorm
import numpy as np

# import Tkinter
from tkinter import *
from tkinter.ttk import *

canvas = None
canvasVehicles = None
fig_photo = None
color = None
currentMeasure = None
interval = None
startTime = None
endTime = None
tabControl = None
vehicles = None
timeVeh = None

from ast import literal_eval

def get_color(color):
    if color == "cool":
        return plt.cm.cool
    elif color == "inferno":
        return plt.cm.inferno
    elif color == "viridis":
        return plt.cm.viridis
    elif color == "greys":
        return plt.cm.Greys
    elif color == "purples":
        return plt.cm.Purples
    elif color == "blues":
        return plt.cm.Blues
    elif color == "plasma":
        return plt.cm.plasma
    elif color == "spring":
        return plt.cm.spring
    elif color == "summer":
        return plt.cm.summer
    elif color == "winter":
        return plt.cm.winter
    elif color == "autumn":
        return plt.cm.autumn
    elif color == "wistia":
        return plt.cm.Wistia
    elif color == "magma":
        return plt.cm.magma
    elif color == "hot":
        return plt.cm.hot
    elif color == "rainbow":
        return plt.cm.rainbow
    elif color == "gist_rainbow":
        return plt.cm.gist_rainbow
    elif color == "brg":
        return plt.cm.brg
    elif color == "hsv":
        return plt.cm.hsv

    return plt.cm.plasma

def draw_figure(canvas, figure, loc=(0, 0)):
    #interface
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)

    # Position: convert from top-left anchor to center anchor
    canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)

    # Unfortunately, there's no accessor for the pointer to the native renderer
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

    return photo

def density_plot(mydata, measure):
    
    if mydata == None:
        return None
    global color
    
    fig = plt.figure(1)
    plt.hist2d(mydata[0], mydata[1], cmap=get_color(color.get()),
               weights=np.zeros_like(mydata[1]) + 1. / mydata[1].size)
    
    plt.xlabel('time (h)')
    if "pagerank" not in measure:
        plt.ylabel(measure+" centrality")
    else:
        plt.ylabel(measure)
    # plt.title('Relative histogram')
    plt.colorbar()

    # Keep this handle alive, or else figure will disappear
    global fig_photo
    global canvas
    fig_x, fig_y = 0, 0
    fig_photo = draw_figure(canvas, fig, loc=(fig_x, fig_y))
    fig_w, fig_h = fig_photo.width(), fig_photo.height()


    #vehicles
    fig1 = plt_veh.figure(2)
    plt_veh.bar(timeVeh, vehicles,  width=0.1,  color=['red'])
    # print(vehicles, timeVeh)

    plt_veh.xlabel('time (h)')
    plt_veh.ylabel("Number of vehicles")
    plt_veh.grid(True)

    # Keep this handle alive, or else figure will disappear
    global fig_photo_veh
    global canvasVehicles
    fig_x, fig_y = 0, 0

    fig_photo_veh = draw_figure(canvasVehicles, fig1, loc=(fig_x, fig_y))
    

def saveFigure():

    global tabControl
    tab_index = tabControl.index(tabControl.select())
    if tab_index == 0:
        f = tkFileDialog.asksaveasfilename(defaultextension=".png")
        if f is None:  # asksaveasfilename return `None` if dialog closed with "cancel".
            return
        if len(f) >= 1:
            plt.savefig(f)
    elif tab_index == 1:
        a = 1
    # plt.show()

def preparing_data(measure):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    x = []
    y = []
    
    
    # end = float(endTime.get())*1000.*60.*60.*60.
    # start = float(startTime.get())*1000.*60.*60.*60.
    # start = 3600000.
    # end = 9000000.

    # mon, sec = divmod(time, 60.)
    # hr, mon = divmod(mon, 60.)
    # print(hr, mon, sec)  # "%d:%02d:%02d" %
    global startTime, endTime
    global vehicles
    global interval
    global timeVeh
    vehicles = []
    timeVeh = []

    start = float(startTime.get())*1000.*60.* 60.
    end = float(endTime.get())*1000.*60.*60.

    print(start, " ", end, " ", interval)
    # time = 9000000./1000./60.

    for row in c.execute("select cast(time as integer) as time,"+measure+" from graphs where time between "+str(start)+" and "+str(end)):
        time = row[0]
        veh = 0
        d = literal_eval(row[1])
        for key, value in d.items():
            t = float(time)/1000./60./60.
            # print((t * 60.)," ",float(interval.get()))
            if (t * 60.) % float(interval.get()):
                x.append(t)
                y.append(float(value))
            veh = veh + 1
        if (t * 60.) % float(interval.get()):
            timeVeh.append(float(time)/1000./60./60.)
            vehicles.append(veh)
    print(vehicles)
    if len(x) >= 1:
        return [np.array(x), np.array(y)]
    return None

def obtainMeasure():

    global endTime, startTime
    if int(endTime.get()) < int(startTime.get()): 
        errorMessage.showerror("Error", "Start time must be before the end time")
    elif (int(interval.get())/60.) >= int(endTime.get()) or (int(interval.get())/60.) >= int(startTime.get()):
        errorMessage.showerror("Error", "Interval must be lower than start/end time")
    else:
        global canvas
        canvas.delete("all")
        global fig_photo
        fig_photo = None
        plt.close()

        global canvasVehicles
        canvasVehicles.delete("all")
        global fig_photo_veh
        fig_photo_veh = None
        plt_veh.close()

        global currentMeasure
        density_plot(preparing_data(currentMeasure.get()), currentMeasure.get())

        global vehicles
        vehicles = None

def window_frame():
    window = Tk()
    window.style = Style()
    window.style.theme_use("clam")
    window.geometry('1000x580')
    window.title("Graph visual rhythm")

    rootPanel = Frame(window)
    rootPanel.pack(side='left', fill='both', expand=1)

    sidebar = Frame(rootPanel, height=400, width=400)
    sidebar.pack(side="left", fill=Y, expand=1)

    var1 = StringVar()
    labelColor = Label(window, textvariable=var1)
    var1.set("Color scheme")
    labelColor.place(x=30, y=40)

    global color
    color = Combobox(window)
    color['values'] = ("cool", "plasma", "magma", "viridis", "inferno", "greys", "purples", "spring", "summer", "autumn", "winter",
     "Wistia", "hot", "rainbow", "gist_rainbow", "brg", "hsv")
    color.current(1) 
    color.place(bordermode=OUTSIDE, height=30, width=200, x=30, y=60)

    var2 = StringVar()
    labelMeasure = Label(window, textvariable=var2)
    var2.set("Measure")
    labelMeasure.place(x=30, y=110)

    global currentMeasure
    currentMeasure = Combobox(window)
    currentMeasure['values'] = (
        "degree centrality", "closeness centrality", "betweenness centrality", "pagerank", "harmonic centrality", "local efficiency", "global efficiency", "maximal matching")
    currentMeasure.current(0)
    currentMeasure.place(bordermode=OUTSIDE, height=30, width=200, x=30, y=130)

    var3 = StringVar()
    labelInterval = Label(window, textvariable=var3)
    var3.set("Interval (minutes)")
    labelInterval.place(x=30, y=180)

    global interval #minutes
    interval = Combobox(window)
    interval['values'] = ("5", "10", "15", "30", "60", "120")
    interval.current(1)
    interval.place(bordermode=OUTSIDE, height=30, width=200, x=30, y=200)

    var4 = StringVar()
    labelStartTime = Label(window, textvariable=var4)
    var4.set("Start time (hours)")
    labelStartTime.place(x=30, y=250)

    global startTime  # hours
    startTime = Combobox(window)
    startTime['values'] = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
                "13", "14", "15", "16", "18", "19", "20", "21", "22", "23")
    startTime.current(1)
    startTime.place(bordermode=OUTSIDE, height=30, width=200, x=30, y=270)

    var5 = StringVar()
    labelStartTime = Label(window, textvariable=var5)
    var5.set("End time (hours)")
    labelStartTime.place(x=30, y=320)

    global endTime #hours
    endTime = Combobox(window)
    endTime['values'] = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11",
                    "12", "13", "14", "15", "16", "18", "19", "20", "21", "22", "23")
    endTime.current(5)
    endTime.place(bordermode=OUTSIDE, height=30, width=200, x=30, y=340)

    button = Button(master=rootPanel, text='run', command=obtainMeasure)
    button.place(bordermode=OUTSIDE, height=30, width=80, x=30, y=475)

    #only runs using python 3
    w, h = 680, 500
    global tabControl
    tabControl = ttk.Notebook(window,width=w, height=h)          # Create Tab Control
    tab1 = ttk.Frame(tabControl)            # Create a tab
    tab2 = ttk.Frame(tabControl)

    tabControl.add(tab1, text='gvr')      # Add the tab
    tabControl.add(tab2, text='vehicles')      # Add the tab
    tabControl.place(x=280, y=30)  # Pack to make visible

    global canvas 
    canvas = Canvas(tab1, background="white", width=w, height=h)
    canvas.place(x=0, y=0)

    global canvasVehicles 
    canvasVehicles = Canvas(tab2, background="white", width=w, height=h)
    canvasVehicles.place(x=0, y=0)

    # photos = ["1.png","2.png"]
    # def slideShow():
    #     img = next(photos)
    #     displayCanvas.config(image=img)
    #     root.after(50, slideShow) # 0.05 seconds

    saveHistogram = Button(master=window, text='save', command=saveFigure)
    saveHistogram.place(bordermode=OUTSIDE, height=30, width=80, x=150, y=475)

    window.mainloop()

if __name__ == "__main__":
    
    window_frame()
    
    sys.stdout.flush()
