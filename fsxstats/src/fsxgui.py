# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#!/usr/bin/python

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from pandastable import Table
import configparser
import pandas as pd
import io
import os

from pathlib import Path

# In[1]:
# Initialisation, setpath and create/load config file
home = str(Path.home())
path = home+'/.fsxgui'
config_default = '/fsxgui.conf'
if not os.path.exists(path):
    os.mkdir(path)

    
configfile = path+config_default
config = configparser.ConfigParser()

if not os.path.isfile(configfile):
    defaultdict = {'mainpath': home+'/Documents/',
                   'flightdata': home+'/Documents/',
                   'flightvideo': home+'/Documents/',
                   'fsxdatafile': 'FSXdata.csv',
                   'fsxaircraftlib': 'FSXcraftlib.csv',
                   'fsxairportlib': 'FSXportlib.csv'}

    # Create the configuration file as it doesn't exist yet
    cfgfile = open(configfile, "w")

    # Add content to the file
    config.add_section('File_Paths')
    config.set('File_Paths', 'mainpath', defaultdict['mainpath'])
    config.set('File_Paths', 'flightdata', defaultdict['flightdata'])
    config.set('File_Paths', 'flightvideo', defaultdict['flightvideo'])
    
    config.add_section('File_Names')
    config.set('File_Names', 'fsxdatafile', defaultdict['fsxdatafile'])
    
    config.add_section('LIBRARIES')
    config.set('LIBRARIES', 'fsxaircraftlib', defaultdict['fsxaircraftlib'])
    config.set('LIBRARIES', 'fsxairportlib', defaultdict['fsxairportlib'])
    config.write(cfgfile)
    cfgfile.close()


config.read(configfile)
mainpath = config.get('File_Paths', 'mainpath')
flightdata = config.get('File_Paths', 'flightdata')
flightvids = config.get('File_Paths', 'flightvideo')

flightloginfo = mainpath+config.get('File_Names', 'fsxdatafile')

#craftlib = path+config.get('LIBRARIES', 'fsxaircraftlib')
#portlib = path+config.get('LIBRARIES', 'fsxairportlib')
    
# In[2]:
# Load in data ready for viewing and editing
# Load in data for use later in programme


#fsxdata = pd.read_csv(flightloginfo)

# In[3]
# defintions for programme backend (must be called within GUI)
def load_data():
    try:
        fsxdata = pd.read_csv(flightloginfo)
    except:
        tk.messagebox.showerror('Info', 'Something went wrong, please check config and file name.')
    
    clear_data()
    fsxdataview['column'] = list(fsxdata.columns)
    fsxdataview['show'] = 'headings'
    for column in fsxdataview['column']:
        fsxdataview.heading(column, text=column)
    
    df_rows = fsxdata.to_numpy().tolist()
    for row in df_rows:
        fsxdataview.insert('', 'end', values = row)
    return None

def clear_data():
    fsxdataview.delete(*fsxdataview.get_children())
    return None



# Entry for flight data
def datasubmit():
    
    return None


# In[4]
# Easthetics
# Constants and easthetic params
windowdim = '1250x600'
positiondict = {}

inputheadings = ['Continent', 'IOC Code', 'Airport', 'City', 'Country', 'FSX Flight PLan', 'Data File', 'Start Time',
                 'End Time', 'Duration', 'Completed', 'Aircraft', 'TO Vid', 'L Vid']
inputwindowdict = {'IEOC':5,
                   'FLP':7,
                   'Dur': 8,
                   'Standard': 12,
                   'Short': 4,
                   'border':2,}

# In[5]
# Main GUI setup
root = tk.Tk()
root.title('Flight Sim Stats Viewer')
root.geometry(windowdim)

wrapper1 = tk.LabelFrame(root, text='Flight Information')
wrapper2 = tk.LabelFrame(root, text='Submit Flight Details')
wrapper3 = tk.LabelFrame(root, text='View Data and video')

wrapper1.pack(fill='both', expand='yes', padx=20, pady=10)
wrapper2.pack(fill='both', expand='yes', padx=20, pady=10)
wrapper3.pack(fill='both', expand='yes', padx=20, pady=10)


# In[6]
#### Wrapper 1 Data view and information ####

fsxdataview = ttk.Treeview(wrapper1)
fsxdataview.place(relheight=1, relwidth=1)

dataviewscrolly = tk.Scrollbar(wrapper1, orient='vertical', command=fsxdataview.yview)
dataviewscrollx = tk.Scrollbar(wrapper1, orient='horizontal', command=fsxdataview.xview)
fsxdataview.configure(xscrollcommand=dataviewscrollx.set, yscrollcommand=dataviewscrolly.set)
dataviewscrollx.pack(side='bottom', fill='x')
dataviewscrolly.pack(side='right', fill='y')


load_data()
#pt = Table(root)
#pt.pack()
#pt.show


# In[7]
#### Wrapper 2 Data submition ####
# Data entrypoints
Continent_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Continent_input.insert(0, inputheadings[0])
                         
IOC_code_input = tk.Entry(wrapper2, width=inputwindowdict['IEOC'], borderwidth=inputwindowdict['border'])
IOC_code_input.insert(0, inputheadings[1])

Airportname_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Airportname_input.insert(0, inputheadings[2])

City_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
City_input.insert(0, inputheadings[3])

Country_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Country_input.insert(0, inputheadings[4])

FlightPLan_input = tk.Entry(wrapper2, width=inputwindowdict['FLP'], borderwidth=inputwindowdict['border'])
FlightPLan_input.insert(0, inputheadings[5])

FlightDataFile_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
FlightDataFile_input.insert(0, inputheadings[6])

Starttime_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Starttime_input.insert(0, inputheadings[7])

Endtime_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Endtime_input.insert(0, inputheadings[8])

Duration_input = tk.Entry(wrapper2, width=inputwindowdict['Dur'], borderwidth=inputwindowdict['border'])
Duration_input.insert(0, inputheadings[9])

Completed_input = tk.Entry(wrapper2, width=inputwindowdict['Short'], borderwidth=inputwindowdict['border'])
Completed_input.insert(0, inputheadings[10])

Aircraft_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Aircraft_input.insert(0, inputheadings[11])

FlightTOVideo_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
FlightTOVideo_input.insert(0, inputheadings[12])

FlightLVideo_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
FlightLVideo_input.insert(0, inputheadings[13])


Continent_input.grid(row=1, column = 0)
IOC_code_input.grid(row=1, column = 1)
Airportname_input.grid(row=1, column = 2)
City_input.grid(row=1, column = 3)
Country_input.grid(row=1, column = 4)
FlightPLan_input.grid(row=1, column = 5)
FlightDataFile_input.grid(row=1, column = 6)
Starttime_input.grid(row=1, column = 7)
Endtime_input.grid(row=1, column = 8)
Duration_input.grid(row=1, column = 9)
Completed_input.grid(row=1, column = 10)
Aircraft_input.grid(row=1, column = 11)
FlightTOVideo_input.grid(row=1, column = 12)
FlightLVideo_input.grid(row=1, column = 13)




# Bottons
submit = tk.Button(wrapper2, text='Submit', command=lambda: datasubmit())
submit.grid(row=3, column=0)

# In[8]
#### Wrapper 3 Load additional data and videos etc ####
LoaddataBt = tk.Button(wrapper3, text='Load/reload data', command=lambda: load_data())
LoaddataBt.grid(row=0, column = 0)

# In[9]
#### Run main loop ####

# Code to add widgets will go here...
root.mainloop()