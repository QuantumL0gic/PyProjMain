#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 00:31:03 2021

Graphic User interface for Handicap calculations using the World Handicap System

Next steps:
    Clean up code for hcap gui (this code is taken from fsxgui)
    look at displaying and inputing data.

@author: matexp
"""
import sys
import io
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
#from pandastable import Table
import configparser
import pandas as pd
import numpy as np
from pathlib import Path
import configparser

sys.path.append(os.path.abspath('/home/matexp/PyProj/hcap_calc/src'))
import init
import hcapimporter as hi
import hcapcalcs_main as hcalc


# In[0]
##############################################################################
### Setup directories and input arguments ###
##############################################################################
home = str(Path.home())

platform = 'Test' # Test=Testing during development home=Home deirectory for user

if platform == 'Test':    
    path = home+'/PyProj/hcap_calc/'
elif platform == 'home':    
    path = home+'/Documents/'

data = path+'.hcap/'
config_default = 'hcap.conf'

importfromfile = 'Y'
if importfromfile == 'Y':
    course_inf = path+'data/Course_Ratings_001.csv'
    score_inf = path+'data/GolfScores_001.csv'


calc_noninclusive = 'Y' # provide a handicap index for non inclusive rounds within the handicap index calculations ie half rounds that have been paired.

# In[1]
##############################################################################
### Initialisation and import of data ###
##############################################################################
### Initialise for first time use or load available data files (init.py) ###
######################################
file_score, file_hidx, file_course_rat, dat_score, dat_course, dat_direction, dat_tee = init.initialise(path, data, config_default, platform)

### Import data from external sources (hcapimorter.py) ###

    
# In[2]:
##############################################################################
### Defined routines for GUI interactions ###
##############################################################################
### Load data for handicap index file and generate table view ###
def load_data(dat_hcap):
    try:
        dat_hcap = dat_hcap #pd.read_csv(file_hidx)
    except:
        tk.messagebox.showerror('Info', 'Something went wrong, please check config file and file exists.')
    
    clear_data()
    hidxdataview['column'] = list(dat_hcap.columns)
    hidxdataview['show'] = 'headings'
    for column in hidxdataview['column']:
        hidxdataview.heading(column, text=column)
    
    df_rows = dat_hcap.to_numpy().tolist()
    for row in df_rows:
        hidxdataview.insert('', 'end', values = row)
    return None
### Clear data from the table view ###
def clear_data():
    hidxdataview.delete(*hidxdataview.get_children())
    return None

### Entry for score data ###
def datasubmit():
    
    return None

### Import data from csv files ###
def dataimport(): #data, dat_score, score_inf, dat_course, course_inf
    if importfromfile == 'Y':
        dat_score_tmp = hi.import_scores(data, dat_score, score_inf) # Import score data
        dat_course_tmp = hi.import_courseinfo(data, dat_course, course_inf) # Import course data
        
        dat_hcap = hcalc.diff_calculator(dat_score_tmp, dat_course_tmp, dat_direction) # Generate score differentials 
        dat_hcap = hcalc.calc_hidx_cidx(dat_hcap, calc_noninclusive) # Generate handicap index and course index info
        load_data(dat_hcap)
    return None

# In[3]


# In[4]
##############################################################################
### Easthetics ###
##############################################################################
### Constants and easthetic params for gui ###
windowdim = '1250x600'
positiondict = {}

### input box sizes ###
inputwindowdict = {'IEOC':5,
                   'FLP':7,
                   'Dur': 8,
                   'Standard': 12,
                   'Short': 4,
                   'border':2,}

### Input box labels ###
inputheadings = ['Date', 'Course', 'Tee', 'Direction', 'Score']

# In[5]
##############################################################################
### Main GUI setup ###
##############################################################################
### Setup main window with tabs and set wrappers ###
######################################
### Main parent window ###
root = tk.Tk()
root.title('Handicap Index Application')
root.geometry(windowdim)

### Add tab control and tabs ###
tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Handicap Index')
tabControl.add(tab2, text='Course Ratings')
tabControl.add(tab3, text='Analysis')

tabControl.pack(expand=1, fill='both')

### Add internal tab wrappers for input and viewing data ###
wrapper1 = tk.LabelFrame(tab1, text='Handicap Viewer')
wrapper2 = tk.LabelFrame(tab1, text='Submit Score')
wrapper3 = tk.LabelFrame(tab1, text='Analysis Views')

wrapper1.pack(fill='both', expand='yes', padx=20, pady=10)
wrapper2.pack(fill='both', expand='yes', padx=20, pady=10)
wrapper3.pack(fill='both', expand='yes', padx=20, pady=10)


ttk.Label(tab2, text='Not functional yet').grid(column=0, row=0, padx=30, pady=30)
ttk.Label(tab3, text='Not functional yet').grid(column=0, row=0, padx=30, pady=30)

# In[6]
##############################################################################
### Tab 1 - Handicap Index view, score submition, importing of data  ###
##############################################################################
### Wrapper 1 Data view and information ###
######################################
hidxdataview = ttk.Treeview(wrapper1)
hidxdataview.place(relheight=1, relwidth=1)

dataviewscrolly = tk.Scrollbar(wrapper1, orient='vertical', command=hidxdataview.yview)
dataviewscrollx = tk.Scrollbar(wrapper1, orient='horizontal', command=hidxdataview.xview)
hidxdataview.configure(xscrollcommand=dataviewscrollx.set, yscrollcommand=dataviewscrolly.set)
dataviewscrollx.pack(side='bottom', fill='x')
dataviewscrolly.pack(side='right', fill='y')

## !!! Add in loading of handicap data from file if file exists !!!
#load_data(dat_hcap)
#pt = Table(root)
#pt.pack()
#pt.show
# In[7]
######################################
#### Wrapper 2 Data submition ####
######################################
### Data entrypoints ###
Date_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Date_input.insert(0, inputheadings[0])
                         
Course_input = tk.Entry(wrapper2, width=inputwindowdict['IEOC'], borderwidth=inputwindowdict['border'])
Course_input.insert(0, inputheadings[1])

Tee_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Tee_input.insert(0, inputheadings[2])

Direction_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Direction_input.insert(0, inputheadings[3])

Score_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Score_input.insert(0, inputheadings[4])

Date_input.grid(row=1, column = 0)
Course_input.grid(row=1, column = 1)
Tee_input.grid(row=1, column = 2)
Direction_input.grid(row=1, column = 3)
Score_input.grid(row=1, column = 4)

### Bottons for submiting and importing data ###
submit = tk.Button(wrapper2, text='Submit', command=lambda: datasubmit()) # !!! Add functionality !!!
submit.grid(row=3, column=0)
importdata = tk.Button(wrapper2, text='Import from file', command=lambda: dataimport()) #data, dat_score, score_inf, dat_course, course_inf
importdata.grid(row=3, column=1)

# In[8] 
###################################### !!! Move this to tab 3 for analysis !!!
#### Wrapper 3 Load additional data and videos etc ####
######################################
LoaddataBt = tk.Button(wrapper3, text='Load/reload data', command=lambda: load_data())
LoaddataBt.grid(row=0, column = 0)

# In[9]
#### Run main loop ####

# Code to add widgets will go here...
root.mainloop()