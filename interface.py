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

import pandas as pd
import seaborn as sns
# plt.style.use('seaborn')

canvas = None
canvasVehicles = None
canvasMean = None
canvasMax = None
fig_photo = None
color = None
currentMeasure = None
interval = None
startTime = None
endTime = None
tabControl = None
vehicles = None
timeVeh = None
mean = None
maxMeasure = None

fig_photo_scat = None
canvasScatterPlot = None
canvasLog = None
fig_photo_log = None

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

    global startTime, endTime
    global interval

    start = float(startTime.get())*60.
    end = float(endTime.get())*60.

    bins = (end - start)/(float(interval.get()))
    
    fig = plt.figure(1)

    plt.hist2d(mydata[0], mydata[1], cmap=get_color(color.get()), 
               weights=(np.zeros_like(mydata[1]) + 1.) / mydata[1].size, bins=bins)
    
    plt.xlabel('time (h)')
    if "pagerank" not in measure:
        plt.ylabel(measure+" centrality")
    else:
        plt.ylabel(measure)
    # plt.title('Relative histogram')
    plt.grid(True)
    plt.colorbar()

    hexbin(mydata,measure)

    # Keep this handle alive, or else figure will disappear
    global fig_photo
    global timeVeh
    global canvas
    fig_x, fig_y = 50, 0
    fig_photo = draw_figure(canvas, fig, loc=(fig_x, fig_y))
    fig_w, fig_h = fig_photo.width(), fig_photo.height()

    #mean measure
    fig2 = plt.figure(3)
    plt.stem(timeVeh, mean,  use_line_collection=True)

    plt.xlabel('time (h)')
    plt.ylabel("Mean "+measure)
    plt.grid(True)

    global fig_photo_mean
    global canvasMean
    fig_x, fig_y = 50, 0

    fig_photo_mean = draw_figure(canvasMean, fig2, loc=(fig_x, fig_y))

    
    fig3 = plt.figure(4)
    plt.stem(timeVeh, maxMeasure,  use_line_collection=True)

    plt.xlabel('time (h)')
    plt.ylabel("Maximum "+measure)
    plt.grid(True)


    global fig_photo_max
    global canvasMax
    fig_x, fig_y = 50, 0

    fig_photo_max = draw_figure(canvasMax, fig3, loc=(fig_x, fig_y))


    #vehicles
    fig1 = plt.figure(6)
    plt.stem(timeVeh, vehicles,  use_line_collection=True)
    # print(vehicles, timeVeh)

    plt.xlabel('time (h)')
    plt.ylabel("Number of vehicles")
    plt.grid(True)

    # Keep this handle alive, or else figure will disappear
    global fig_photo_veh
    global canvasVehicles
    fig_x, fig_y = 50, 0

    fig_photo_veh = draw_figure(canvasVehicles, fig1, loc=(fig_x, fig_y))


    global fig_photo_scat
    global canvasScatterPlot
    fig_x, fig_y = 50, 0

    fig4 = plt.figure(5)

    df = pd.DataFrame( mydata[0], mydata[1])

    # plt.plot( 'x', 'y', data=df, linestyle='none', marker='o', markersize=0.7, alpha=0.5, color="purple")
    plt.plot(mydata[0], mydata[1], 'ko',  markersize=4, alpha=0.5, color='purple')
    plt.xlabel('time (h)')
    plt.ylabel(measure)
    plt.grid(True)

    fig_photo_scat = draw_figure(canvasScatterPlot, fig4, loc=(fig_x, fig_y))


def hexbin(mydata, measure):

    x = mydata[0]
    y = mydata[1]

    xmin = x.min()
    xmax = x.max()
    ymin = y.min()
    ymax = y.max()

    global canvasLog
    global color
    global fig_photo_log 

    fig = plt.figure(2)
    hb = plt.hexbin(x, y, bins='log', gridsize=30, cmap=get_color(color.get()))
    plt.axis([xmin, xmax, ymin, ymax])
    plt.xlabel('time (h)')
    if "pagerank" not in measure:
        plt.ylabel(measure+" centrality")
    else:
        plt.ylabel(measure)
    cb = plt.colorbar(hb)
    cb.set_label('log10(N)')
    plt.grid(True)

    fig_x, fig_y = 50, 0

    fig_photo_log = draw_figure(canvasLog, fig, loc=(fig_x, fig_y))

def saveFigure():

    global tabControl
    global plt
    tab_index = tabControl.index(tabControl.select())

    plt.figure(tab_index+1)
    f = tkFileDialog.asksaveasfilename(defaultextension=".png")
    if f is None:  # asksaveasfilename return `None` if dialog closed with "cancel".
        return
    if len(f) >= 1:
        plt.savefig(f)

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
    global maxMeasure
    global mean

    maxMeasure = []
    mean = []
    vehicles = []
    timeVeh = []

    start = float(startTime.get())*1000.*60.* 60.
    end = float(endTime.get())*1000.*60.*60.

    print(start, " ", end, " ", interval)
    # time = 9000000./1000./60.

    # :(
    m = measure
    if "betweenness" in measure:
        m = "betweeness"
    elif "local" in measure:
        m = "local_efficiency"
    elif "global" in measure:
        m = "global_efficiency"
    elif "maximal" in measure:
        m = "maximal_matching"
    elif "harmonic" in measure:
        m = "harmonic_centrality"
    print(m)
    it = float(interval.get()) * 1000. * 60.
    for row in c.execute("select cast(time as integer) as time,"+m+" from graphs where time between "+str(start)+" and "+str(end)):
     
        time = float(row[0])
        veh = 0
        d = literal_eval(row[1])
        sum = 0.
        maxValue = 0.
        t = float(time)
        print(d)
        for key, value in d.items():
            if t  % it == 0:
                x.append(t/1000./60./60.)
                y.append(float(value))
                veh = veh + 1
                sum += float(value)
                if maxValue < float(value):
                    maxValue = float(value)
        if t % it == 0:

            timeVeh.append(t/1000./60./60.)
            vehicles.append(veh)
            m = float(sum)/float(veh)
            mean.append(m)
            maxMeasure.append(maxValue)
    if len(x) >= 1:
        return [np.array(x), np.array(y)]
    return None

def obtainMeasure():

   
    global endTime, startTime
    global interval

    conv = float(interval.get())/60.
    print(conv," ",endTime.get()," ",startTime.get())
    if float(endTime.get()) < float(startTime.get()): 
        errorMessage.showerror("Error", "Start time must be before the end time")
    elif conv >= float(endTime.get()) or conv > (float(endTime.get()) - float(startTime.get())):
        errorMessage.showerror("Error", "Interval must be lower than start/end time")
    else:

        global canvas
        canvas.delete("all")
        global fig_photo
        plt.close(1)  
        fig_photo = None
      

        global canvasVehicles
        canvasVehicles.delete("all")
        global fig_photo_veh
        plt.close(6)
        fig_photo_veh = None

        global canvasMax
        canvasMax.delete("all")
        global fig_photo_max
        plt.close(4)
        fig_photo_max = None

        global canvasMean
        canvasMean.delete("all")
        global fig_photo_mean
        plt.close(3)
        fig_photo_mean = None

        global canvasScatterPlot
        canvasScatterPlot.delete("all")
        global fig_photo_scat
        plt.close(5)
        fig_photo_scat = None

        global canvasLog
        canvasLog.delete("all")
        global fig_photo_log
        plt.close(2)
        fig_photo_log = None

        global currentMeasure
        density_plot(preparing_data(currentMeasure.get()), currentMeasure.get())

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
    interval['values'] = ("1", "5", "10", "15", "30", "60", "120")
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
    tab3 = ttk.Frame(tabControl)
    tab4 = ttk.Frame(tabControl)
    tab5 = ttk.Frame(tabControl)
    tab6 = ttk.Frame(tabControl)

    tabControl.add(tab1, text='gvr')     
    tabControl.add(tab2, text='gvr-log')     
    tabControl.add(tab3, text='mean')     
    tabControl.add(tab4, text='max')      
    tabControl.add(tab5, text='scatter')     
    tabControl.add(tab6, text='vehicles')
    tabControl.place(x=280, y=30)  # Pack to make visible

    global canvas 
    canvas = Canvas(tab1, background="white", width=w, height=h)
    canvas.place(x=0, y=0)

    global canvasLog
    canvasLog = Canvas(tab2, background="white", width=w, height=h)
    canvasLog.place(x=0, y=0)

    global canvasMean
    canvasMean = Canvas(tab3, background="white", width=w, height=h)
    canvasMean.place(x=0, y=0)

    global canvasMax
    canvasMax = Canvas(tab4, background="white", width=w, height=h)
    canvasMax.place(x=0, y=0)

    global canvasScatterPlot
    canvasScatterPlot = Canvas(tab5, background="white", width=w, height=h)
    canvasScatterPlot.place(x=0, y=0)

    global canvasVehicles 
    canvasVehicles = Canvas(tab6, background="white", width=w, height=h)
    canvasVehicles.place(x=0, y=0)
  
    saveHistogram = Button(master=window, text='save', command=saveFigure)
    saveHistogram.place(bordermode=OUTSIDE, height=30, width=80, x=150, y=475)

    window.mainloop()

if __name__ == "__main__":
    
    window_frame()
    
    sys.stdout.flush()
