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
from ttkwidgets import CheckboxTreeview
#from pandastable import Table
import configparser
import pandas as pd
import numpy as np
from pathlib import Path

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

#importfromfile = 'Y'
#if importfromfile == 'Y':
#    course_inf = path+'data/Course_Ratings_001.csv'
#    score_inf = path+'data/GolfScores_001.csv'

calc_noninclusive = 'Y' # provide a handicap index for non inclusive rounds within the handicap index calculations ie half rounds that have been paired.

# In[1]
##############################################################################
### Initialisation and import of data ###
##############################################################################
### Initialise for first time use or load available data files (init.py) ###
######################################
file_score, file_hidx, file_course_rat, dat_score, dat_course, dat_direction, dat_tee = init.initialise(path, data, config_default, platform)


score_entries = []
course_entries = []
course_list = []
tee_list = dat_tee['Tee'].to_list()
direction_list = dat_direction['Direction'].to_list()
# In[2]:
##############################################################################
### Defined routines for GUI interactions ###
##############################################################################
### Tab 2 - Course Rating tab functionality ###
######################################
### Load data from Course Rating data
def load_course_data(course_info):
    '''
    try:
        dat_hcap = pd.read_csv(file_hidx)
    except:
        tk.messagebox.showerror('Info', 'Something went wrong, please check config file and file exists.')
    '''
    # Update table with entries from imported or manual entry
    clear_data_t2()
    cratdataview['column'] = list(course_info.columns)
    cratdataview['show'] = 'headings'
    for column in cratdataview['column']:
        cratdataview.heading(column, text=column)
    
    df_rows = course_info.to_numpy().tolist()
    for row in df_rows:
        cratdataview.insert('', 'end', values = row)
    # Update global variables with new tables
    global dat_course
    dat_course = course_info
    getcourses()
    SetCoursedrop()
    return None
### Clear data from the table view ###
def clear_data_t2():
    cratdataview.delete(*cratdataview.get_children())
    return None

### Course information importer ###
def courseimport(): #data, dat_score, score_inf, dat_course, course_inf
    # Select file to import
    course_inf = filedialog.askopenfilename(initialdir=home, title = 'Import Course Info File',
                                           filetypes=(('CSV File', '*.csv'),('All Files', '*.*')))
    # Import data to pandas df
    dat_course_tmp = hi.import_courseinfo(data, dat_course, course_inf) # Import course data
    # Append rows to global course data
    #dat_course.append(dat_course_tmp)
    # Load data into treeview tab 2
    load_course_data(dat_course_tmp)
    return None

### Submit course information ### !!! Add functionality !!!
def submitcourse():
    return None
######################################
### Tab 1 - Handicap Index tab functionality ###
######################################
### Load data for handicap index file and generate table view ###
def read_hidx():
    hidx_dat = pd.read_csv(file_hidx)
    return hidx_dat

def load_data(hidx_dat):
    '''
    try:
        dat_hcap = pd.read_csv(file_hidx)
    except:
        tk.messagebox.showerror('Info', 'Something went wrong, please check config file and file exists.')
    '''
    # Generate handicap index
    
    # Setup hanidcap index table for viewing
    hidx_datview = hidx_dat.drop(['PairingIdx', 'Inclusion'], axis=1)
    clear_data()
    hidxdataview['column'] = list(hidx_datview.columns)
    hidxdataview['show'] = 'headings'
    for column in hidxdataview['column']:
        hidxdataview.heading(column, text=column)
    
    df_rows = hidx_datview.to_numpy().tolist()
    for row in df_rows:
        hidxdataview.insert('', 'end', values = row)
    global dat_score, dat_hcap
    dat_score = hidx_dat.iloc[:,0:5]
    dat_hcap = hidx_dat
    return None
### Clear data from the table view ###
def clear_data():
    hidxdataview.delete(*hidxdataview.get_children())
    return None

### Entry for score data ### !!! Add functionality !!!
def submitscore():
    coursename = score_entries[1].get() # Get Course name
    if nocoursename(coursename) == True: # Check course is in course rating list
        score_ent_tmp = []
        score_len = len(dat_score)
        for i, entry in enumerate(score_entries): # Generate entries for score data file
            score_ent_tmp.append(entry.get())
        dat_score.loc[score_len] = score_ent_tmp
        # Generate tables and load data into treeview tab 1
        hidx_dat = genhidx()
        load_data(hidx_dat)
        ### !!! Clear entries and start new entry list !!! ###
    return None

def submitdrop():
    datein = Date_input.get()
    coursein = Course_input.get()
    teein = Tee_input.get()
    dirin = Direction_input.get()
    scorein = Score_input.get()
    inputlist = [datein, coursein, teein, dirin, scorein]
    global dat_score
    score_len = len(dat_score)
    dat_score.loc[score_len] = inputlist
    hidx_dat = genhidx()
    load_data(hidx_dat)
    return None

### Import data from csv files ###
# Score data
def scoreimport(): #data, dat_score, score_inf, dat_course, course_inf
    if len(dat_course) < 1:
        nocoursedata()
    else:
        # Select file to import
        score_inf = filedialog.askopenfilename(initialdir=home, title = 'Import Score File',
                                               filetypes=(('CSV File', '*.csv'),('All Files', '*.*')))
        # Import file as pandas df and append rows to global score data variable
        global dat_score
        dat_score = hi.import_scores(data, dat_score, score_inf) # Import score data
        # Generate tables and load data into treeview tab 1
        hidx_dat = genhidx()
        load_data(hidx_dat)
    return None

'''
# Temporary importer for both score and course info
def dataimport(): #data, dat_score, score_inf, dat_course, course_inf
    if importfromfile == 'Y':
        dat_score_tmp = hi.import_scores(data, dat_score, score_inf) # Import score data
        dat_course_tmp = hi.import_courseinfo(data, dat_course, course_inf) # Import course data
        
        dat_hcap = hcalc.diff_calculator(dat_score_tmp, dat_course_tmp, dat_direction) # Generate score differentials 
        dat_hcap = hcalc.calc_hidx_cidx(dat_hcap, calc_noninclusive) # Generate handicap index and course index info
        load_data(dat_hcap)
    return None
'''
######################################
### General functions ###
######################################
### Message box for empty course info table ###
def nocoursedata():
    tk.messagebox.showerror('No Course Data', 'Please update course data or import from file')
    return False

### Mesage box for no specific course info available ###
def nocoursename(name):
    if name not in course_list:
        state = False
        tk.messagebox.showerror('Course Data Not Available', 'Please check the course is present in the course rating tab or update with course info')
    else:
        state = True
    return state
### Get list of courses ###
def getcourses():
    if len(dat_course) > 0:
        global course_list
        course_list = dat_course['Course'].unique()
    return None
### Get list of Tees ###
#def gettees():
#    global tee_list
#    tee_list = dat_tee['Tee'].to_list()
#    return None

### Generate handicap index table ###
def genhidx():
    hidx_dat_tmp = hcalc.diff_calculator(dat_score, dat_course, dat_direction) # Generate score differentials 
    hidx_dat_tmp = hcalc.calc_hidx_cidx(hidx_dat_tmp, calc_noninclusive) # Generate handicap index and course index info
    return hidx_dat_tmp

def SetCoursedrop():
    if len(dat_course) > 0:
        global Course_input
        Course_drop = tk.OptionMenu(wrapper2, Course_input, *course_list)
        Course_drop.grid(row=2, column = 1)
    return None


hcap = genhidx()
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
scoreinputheadings = ['Date', 'Course', 'Tee', 'Direction', 'Score']
courseinputheadings = ['Course', 'Tee', 'Par', 'Rating', 'Bogey Rating', 'Slope', 'Front Par', 'Front Slope', 'Back Par', 'Back Slope']


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

######################################
### Add internal tab wrappers for input and viewing data ###
######################################
### Tab 1 - Handicap Index View and score submition/import ###
wrapper1 = tk.LabelFrame(tab1, text='Handicap Viewer')
wrapper2 = tk.LabelFrame(tab1, text='Submit Score')
#wrapper3 = tk.LabelFrame(tab1, text='Analysis Views')

wrapper1.pack(fill='both', expand='yes', padx=20, pady=10)
wrapper2.pack(fill='both', expand='yes', padx=20, pady=10)
#wrapper3.pack(fill='both', expand='yes', padx=20, pady=10)


### Tab 2 - Course information and submition/import ###
wrapper_t2_1 = tk.LabelFrame(tab2, text='Course Rating Viewer')
wrapper_t2_2 = tk.LabelFrame(tab2, text='Submit Course Information')

wrapper_t2_1.pack(fill='both', expand='yes', padx=20, pady=10)
wrapper_t2_2.pack(fill='both', expand='yes', padx=20, pady=10)

### Tab 3 - View analysis and graphs ###
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
if os.path.isfile(data+file_hidx):
    dat_hcap = read_hidx()
    load_data(dat_hcap)
#load_data(dat_hcap)
#pt = Table(root)
#pt.pack()
#pt.show
# In[7]
######################################
#### Wrapper 2 Data submition ####
######################################
### Data entrypoints ###
for i, header in enumerate(scoreinputheadings):
    score_entry = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    score_entry.grid(row=1, column = i)
    score_entry.insert(0, header)
    score_entries.append(score_entry)

Date_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Date_input.insert(0, scoreinputheadings[0])

### Course input drop down menu ###
Course_input = tk.StringVar()
Course_input.set('None')

#Course_drop = tk.OptionMenu(wrapper2, Course_input, *course_list)

### Tee input frop down menu ###
Tee_input = tk.StringVar()
Tee_input.set('None')

Tee_drop = tk.OptionMenu(wrapper2, Tee_input, *tee_list)

### Play Direction input drop down menu ###
Direction_input = tk.StringVar()
Direction_input.set('None')

Direction_drop = tk.OptionMenu(wrapper2, Direction_input, *direction_list)

### Score input ###
Score_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
Score_input.insert(0, scoreinputheadings[4])


Date_input.grid(row=2, column = 0)
#Course_drop.grid(row=2, column = 1)
Tee_drop.grid(row=2, column = 2)
Direction_drop.grid(row=2, column = 3)

Score_input.grid(row=2, column = 4)

### Bottons for submiting and importing data ###
submit = tk.Button(wrapper2, text='Submit Score', command=submitscore) # !!! Add functionality !!!
submit.grid(row=3, column=0)
importdata = tk.Button(wrapper2, text='Import Scores ff', command=scoreimport) #data, dat_score, score_inf, dat_course, course_inf
importdata.grid(row=3, column=1)

submitdrop = tk.Button(wrapper2, text='Submit Score(Drop)', command=submitdrop) # !!! Add functionality !!!
submitdrop.grid(row=3, column=3)

#Course_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
#Course_input.insert(0, scoreinputheadings[1])

#Tee_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
#Tee_input.insert(0, scoreinputheadings[2])

#Direction_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
#Direction_input.insert(0, scoreinputheadings[3])

#Course_input.grid(row=2, column = 1)
#Tee_input.grid(row=2, column = 2)
#Direction_input.grid(row=2, column = 3)

# In[8] 
###################################### !!! Move this to tab 3 for analysis !!!
#### Wrapper 3 Load additional data and videos etc ####
######################################
#LoaddataBt = tk.Button(wrapper3, text='Load/reload data', command=lambda: load_data())
#LoaddataBt.grid(row=0, column = 0)

# In[9]
##############################################################################
### Tab 2 - Course Rating view, course information submition, importing of data  ###
##############################################################################
### Wrapper 1 Course rating data view and information ###
######################################
cratdataview = ttk.Treeview(wrapper_t2_1)
cratdataview.place(relheight=1, relwidth=1)

cratdatascrolly = tk.Scrollbar(wrapper_t2_1, orient='vertical', command=cratdataview.yview)
cratdatascrollx = tk.Scrollbar(wrapper_t2_1, orient='horizontal', command=cratdataview.xview)
cratdataview.configure(xscrollcommand=cratdatascrollx.set, yscrollcommand=cratdatascrolly.set)
cratdatascrollx.pack(side='bottom', fill='x')
cratdatascrolly.pack(side='right', fill='y')


load_course_data(dat_course)

#load_data(dat_hcap)
#pt = Table(root)
#pt.pack()
#pt.show

# In[10]
######################################
#### Wrapper 2 Data submition ####
######################################
### Data entrypoints ###
CourseName = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseName.insert(0, courseinputheadings[0])
                         
TeeColour = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
TeeColour.insert(0, courseinputheadings[1])

CoursePar = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CoursePar.insert(0, courseinputheadings[2])

CourseRating = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseRating.insert(0, courseinputheadings[3])

CourseBogRating = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseBogRating.insert(0, courseinputheadings[4])

CourseSlope = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseSlope.insert(0, courseinputheadings[5])

CourseFPar = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseFPar.insert(0, courseinputheadings[6])

CourseFSlope = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseFSlope.insert(0, courseinputheadings[7])

CourseBPar = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseBPar.insert(0, courseinputheadings[8])

CourseBSlope = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
CourseBSlope.insert(0, courseinputheadings[9])


CourseName.grid(row=1, column = 0)
TeeColour.grid(row=1, column = 1)
CoursePar.grid(row=1, column = 2)
CourseRating.grid(row=1, column = 3)
CourseBogRating.grid(row=1, column = 4)
CourseSlope.grid(row=1, column = 5)
CourseFPar.grid(row=1, column = 6)
CourseFSlope.grid(row=1, column = 7)
CourseBPar.grid(row=1, column = 8)
CourseBSlope.grid(row=1, column = 9)

### Bottons for submiting and importing data ###
CourseSubmit = tk.Button(wrapper_t2_2, text='Submit', command=lambda: submitcourse()) # !!! Add functionality !!!
CourseSubmit.grid(row=3, column=0)
courseimportdata = tk.Button(wrapper_t2_2, text='Import Course Info', command=courseimport) #data, dat_score, score_inf, dat_course, course_inf
courseimportdata.grid(row=3, column=1)

# In[]
#### Run main loop ####

# Code to add widgets will go here...
root.mainloop()