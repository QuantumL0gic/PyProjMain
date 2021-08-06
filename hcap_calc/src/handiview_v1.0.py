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
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker

sys.path.append(os.path.abspath('/home/matexp/PyProj/hcap_calc/src'))
import init
import hcapimporter as hi
import hcapcalcs_main_v1_0 as hcalc


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


calc_noninclusive = 'Y' # provide a handicap index for non inclusive rounds within the handicap index calculations ie half rounds that have been paired.

# In[1]
##############################################################################
### Initialisation and import of data ###
##############################################################################
### Initialise for first time use or load available data files (init.py) ###
######################################
# Fetch file locations and stored data from config files

file_score, file_hidx, file_course_rat, dat_score, dat_course, dat_hcap, dat_direction, dat_tee = init.initialise(path, data, config_default, platform)

# Set global variables for list entries
scoreselected = []
courseselected = []
scoreidx = []
courseidx = []
course_entries = []
course_list = []
tee_list = dat_tee['Tee'].to_list()
direction_list = dat_direction['Direction'].to_list()
# In[2]:
##############################################################################
### Start the main loop for the application (need to put this into a class) ###
##############################################################################
def main():
##############################################################################
### Defined routines for GUI interactions ###
##############################################################################
### Tab 2 - Course Rating tab functionality ###
### Load data from Course Rating data

######################################
    def load_course_data(course_info):
        # Create list of indexes in table
        tviewidx = []
        # Update table with entries from imported or manual entry
        clear_data_t2()
        
        cratdataview['column'] = list(course_info.columns)
        cratdataview['show'] = 'headings'
        for column in cratdataview['column']:
            cratdataview.heading(column, text=column)
        
        df_rows = course_info.to_numpy().tolist()
        for i, row in enumerate(df_rows):
            cratdataview.insert('', 'end', iid=i, values = row)
            tviewidx.append(i)
        # Update global variables with new tables
        global dat_course, courseidx
        dat_course = course_info
        courseidx = tviewidx
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
    
    ### Submit course information ###
    def submitcourse():
        cname = CourseName.get()
        tcol = TeeCol_drop.get()
        cpar = CoursePar.get()
        crat = CourseRating.get()
        cbograt = CourseBogRating.get()
        cslope = CourseSlope.get()
        cfrat = CourseFPar.get()
        cfslope = CourseFSlope.get()
        cbrat = CourseBPar.get()
        cbslope = CourseBSlope.get()
        inputlist = [cname,
                     tcol,
                     cpar,
                     crat,
                     cbograt,
                     cslope,
                     cfrat,
                     cfslope,
                     cbrat,
                     cbslope]
        try:
            incourse = pd.DataFrame(columns=courseratheaders)
            indata = pd.Series(inputlist, index=incourse.columns)
            incourse = incourse.append(indata, ignore_index=True)
            course_tmp = dat_course
            course_tmp = course_tmp.append(incourse, ignore_index=True)
            course_tmp.sort_values('Course', inplace=True)
            load_course_data(course_tmp)
        except:
            course_tmp = course_tmp.drop(index=(cname, tcol))
            load_course_data(course_tmp)
            tk.messagebox.showerror('Check Course Entry', 'Please check all entry fields and try again.')
        return None
    
    
    def course_entremove():
        course_tmp = dat_course
        course_tmp.drop(courseselected, inplace=True)
        load_course_data(course_tmp)
        # !!! Set rerun of differential calculation but preserve 'Inclusion' field 
        return None
    
    def getcratindex(event):
        rows = cratdataview.selection()
        indexlist = []
        for row in rows:
            index = cratdataview.index(row)
            indexlist.append(index)
        #iid = hidxdataview.identify(event.x, event.y)
        global courseselected
        courseselected = indexlist
        return None
    ######################################
    ### Tab 1 - Handicap Index tab functionality ###
    ######################################
    ### Load data for handicap index file and generate table view ###
    def read_hidx():
        hidx_dat = pd.read_csv(file_hidx)
        return hidx_dat
    
    def load_data(hidx_dat):
        # Create list of indexes in table
        tviewidx = []
        # Setup hanidcap index table for viewing
        hidx_datview = hidx_dat.drop(['PairingIdx', 'Inclusion'], axis=1)
        clear_data()
        hidxdataview['column'] = list(hidx_datview.columns)
        hidxdataview['show'] = 'headings'
        for column in hidxdataview['column']:
            hidxdataview.heading(column, text=column)
        
        df_rows = hidx_datview.to_numpy().tolist()
        for i, row in enumerate(df_rows):
            hidxdataview.insert('', 'end', iid=i, values = row) # !!! Use iid to select items from the database for deletion and minipulation
            tviewidx.append(i)
        global dat_score, dat_hcap, scoreidx
        scoreidx = tviewidx
        dat_score = hidx_dat.iloc[:,0:5]
        dat_hcap = hidx_dat
        plothcapdat()
        return None
    ### Clear data from the table view ###
    def clear_data():
        hidxdataview.delete(*hidxdataview.get_children())
        return None
    
    ### Entry for score data ###
    def submitdrop():
        # Fetch intries
        datein = Date_input.get()
        coursein = Course_drop.get() #Course_input
        teein = Tee_drop.get()
        dirin = Direction_drop.get()
        scorein = Score_input.get()
        inputlist = [datein, coursein, teein, dirin, scorein]
        try:
            inscore = pd.DataFrame(columns=scoreheaders)
            indata = pd.Series(inputlist, index=inscore.columns)
            inscore = inscore.append(indata, ignore_index=True)
            hidx_dat = hcalc.diff_calculator(inscore, dat_course, dat_direction)
        except:
            inscore = pd.DataFrame(columns=scoreheaders)
            hidx_dat = pd.DataFrame(columns=dat_hcap.columns)
            tk.messagebox.showerror('Check Score Entry', 'Please check all entry fields and try again.')
        dat_hcap_tmp = dat_hcap
        dat_hcap_tmp = dat_hcap_tmp.append(hidx_dat)
        dat_hcap_tmp = hcalc.calc_hidx_cidx(dat_hcap_tmp, dat_direction, calc_noninclusive)
        load_data(dat_hcap_tmp)
        return None
    
    def score_entremove():
        hidx_dat = dat_hcap
        hidx_dat.drop(scoreselected, inplace=True)
        hidx_dat = hcalc.calc_hidx_cidx(hidx_dat, dat_direction, calc_noninclusive)
        load_data(hidx_dat)
        return None
    
    def gethidxindex(event):
        rows = hidxdataview.selection()
        indexlist = []
        for row in rows:
            index = hidxdataview.index(row)
            indexlist.append(index)
        #iid = hidxdataview.identify(event.x, event.y)
        global scoreselected
        scoreselected = indexlist
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
            #global dat_score
            dat_score_tmp = hi.import_scores(data, dat_score, score_inf) # Import score data
            # Generate tables and load data into treeview tab 1
            hidx_dat = genhidx(dat_score_tmp)
            load_data(hidx_dat)
        return None
    
    ######################################
    ### Tab 3 - Analysis ###
    ######################################
    def plothcapdat():
        if len(dat_hcap) > 0:
            wid, hig = getplotsize()
            yvals = dat_hcap['Handicap Index'].to_list()
            xvals = dat_hcap['Date'].to_list()
            hidxdatfig = plt.Figure(figsize=(wid, hig), dpi=appdpi)
            ax1 = hidxdatfig.add_subplot(111)
            
            ax1.plot(xvals,yvals, color = 'blue')
            ax1.set_ylim([0, 50])
            ax1.set_xlim([min(xvals), max(xvals)])
            ax1.set_ylabel('Handicap Index')
            ax1.set_xlabel('Date')
            
            #tick_loc = ax1.get_xticks().tolist()
            #ax1.xaxis.set_major_locator(mticker.FixedLocator(tick_loc))
            #ax1.set_xticklabels([date.strftime('%d/%m/%Y') for date in xvals])
            ax1.set_title('Handicap Index Variability')
            
            line1 = FigureCanvasTkAgg(hidxdatfig, wrapper_t3_1)
            line1.draw()
            line1.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        return None
    ######################################
    ### General functions ###
    ######################################
    ### Message box for empty course info table ###
    def nocoursedata():
        tk.messagebox.showerror('No Course Data', 'Please update course data or import from file.')
        return False
    
    ### Mesage box for no specific course info available ###
    def nocoursename(name):
        if name not in course_list:
            state = False
            tk.messagebox.showerror('Course Data Not Available', 'Please check the course is present in the course rating tab or update with course info.')
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
    #    tee_list = dat_course['Tee'].unique()
    #    return None
    
    ### Generate handicap index table ###
    def genhidx(dat_score_tmp):
        hidx_dat_tmp = hcalc.diff_calculator(dat_score_tmp, dat_course, dat_direction) # Generate score differentials 
        hidx_dat_tmp = hcalc.calc_hidx_cidx(hidx_dat_tmp, dat_direction, calc_noninclusive) # Generate handicap index and course index info
        return hidx_dat_tmp
    
    def SetCoursedrop():
        if len(dat_course) > 0:
            #global Course_input
            Course_drop.config(values=tuple(course_list))
            #Course_drop = ttk.Combobox(wrapper2, value=course_list)
            #Course_drop.grid(row=2, column = 1)
            #Course_drop.current(scoreinputheadings[1])
        return None
    
    def SetTeeDrop(e):
        Tee_list_tmp = dat_course.loc[dat_course['Course'] == Course_drop.get()]
        Tee_list_tmp = Tee_list_tmp['Tee'].to_list()
        if len(Tee_list_tmp) > 0:
            Tee_drop.config(values=tuple(Tee_list_tmp))
        else:
            Tee_drop.config(values=None)
            Tee_drop.set(scoreinputheadings[2])
        return None
    
    def getplotsize():
        ploth_pix = round(appwinheight/2)
        ploth_inch = ploth_pix/appdpi
        plotw_inch = ploth_inch*3 #/9)*10
        
        return plotw_inch, ploth_inch
    #hcap = genhidx()
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
    scoreinputheadings = ['DD/MM/YYYY', 'Course', 'Tee', 'Direction', 'Score']
    scoreheaders = ['Date', 'Course', 'Tee', 'Direction', 'Score']
    courseinputheadings = ['Course', 'Tee', 'Par', 'Rating', 'Bogey Rating', 'Slope', 'Front Par', 'Front Slope', 'Back Par', 'Back Slope']
    courseratheaders = ['Course', 'Tee', 'Par', 'Rating',
                                              'Bogey_Rating', 'Slope', 'Front_Par', 'Front_Slope', 'Back_Par', 'Back_Slope']
    
    
    # In[5]
    ##############################################################################
    ### Main GUI setup ###
    ##############################################################################
    ### Setup main window with tabs and set wrappers ###
    ######################################
    ### Main parent window ###
    root = tk.Tk()
    root.title('Handicap Index Application')
    #root.geometry(windowdim)
    
    screenheight = root.winfo_screenheight()
    screenwidth = root.winfo_screenwidth()
    appwinheight = round(screenheight/2)
    appwinwidth = round(screenwidth/2)
    appdpi = root.winfo_fpixels('1i')
    
    appgeom = str(appwinwidth)+'x'+str(appwinheight)
    
    root.geometry(appgeom)
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
    wrapper_t3_1 = tk.LabelFrame(tab3, text='Temporal Graph')
    wrapper_t3_2 = tk.LabelFrame(tab3, text='Analysis Statitics and Tools')
    
    wrapper_t3_1.pack(fill='both', expand='yes', padx=10, pady=0)
    wrapper_t3_2.pack(fill='both', expand='yes', padx=20, pady=10)
    
    # In[6]
    ##############################################################################
    ### Tab 1 - Handicap Index view, score submition, importing of data  ###
    ##############################################################################
    ### Wrapper 1 Data view and information ###
    ######################################
    hidxdataview = ttk.Treeview(wrapper1)
    #hidxdataview.place(relheight=1, relwidth=1)
    hidxdataview.pack(fill='both', expand=1) #, relheight=1, relwidth=1)
    
    dataviewscrolly = tk.Scrollbar(wrapper1, orient='vertical', command=hidxdataview.yview)
    dataviewscrollx = tk.Scrollbar(wrapper1, orient='horizontal', command=hidxdataview.xview)
    hidxdataview.configure(xscrollcommand=dataviewscrollx.set, yscrollcommand=dataviewscrolly.set)
    dataviewscrollx.pack(side='bottom', fill='x')
    dataviewscrolly.pack(side='right', fill='y')
    
    ### Load handicap data ###
    load_data(dat_hcap)
    
    ### Bindings for treview table ###
    hidxdataview.bind('<ButtonRelease-1>', gethidxindex)
    # In[7]
    ######################################
    #### Wrapper 2 Data submition ####
    ######################################
    ### Date input ###
    Date_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    Date_input.insert(0, scoreinputheadings[0])
    
    ### Course input drop down menu ###
    Course_drop = ttk.Combobox(wrapper2, value=course_list)
    Course_drop.set(scoreinputheadings[1]) #current
    
    ### Tee input frop down menu ###
    Tee_drop = ttk.Combobox(wrapper2, value=None)
    Tee_drop.set(scoreinputheadings[2]) #current
    
    ### Play Direction input drop down menu ###
    Direction_drop = ttk.Combobox(wrapper2, value=tuple(direction_list))
    Direction_drop.set(scoreinputheadings[3]) #current
    
    ### Score input ###
    Score_input = tk.Entry(wrapper2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    Score_input.insert(0, scoreinputheadings[4])
    
    ### Position input widgets ###
    Date_input.grid(row=2, column = 0)
    Course_drop.grid(row=2, column = 1)
    Tee_drop.grid(row=2, column = 2)
    Direction_drop.grid(row=2, column = 3)
    Score_input.grid(row=2, column = 4)
    
    ### Bottons for submiting and importing data ###
    submitdrop = tk.Button(wrapper2, text='Submit Score', command=submitdrop)
    submitdrop.grid(row=3, column=0)
    
    importdata = tk.Button(wrapper2, text='Import Scores ff', command=scoreimport) #data, dat_score, score_inf, dat_course, course_inf
    importdata.grid(row=3, column=1)
    
    removescore = tk.Button(wrapper2, text='Remove Entry', command=score_entremove) #data, dat_score, score_inf, dat_course, course_inf
    removescore.grid(row=3, column=4)
    
    ### Bindings for drop down selection ###
    Course_drop.bind('<<ComboboxSelected>>', SetTeeDrop)
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
    
    ### Load course data from initialisation ###
    load_course_data(dat_course)
    
    ### Bind treeview selection for removal/editing of entry ###
    cratdataview.bind('<ButtonRelease-1>', getcratindex)
    # In[10]
    ######################################
    #### Wrapper 2 Data submition ####
    ######################################
    ### Course Name entry ###
    CourseName = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseName.insert(0, courseinputheadings[0])
    
    ### Tee Colour entry###
    TeeCol_drop = ttk.Combobox(wrapper_t2_2, value=tuple(tee_list))
    TeeCol_drop.set(scoreinputheadings[2]) #current
    
    ### Course Par entry ###
    CoursePar = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CoursePar.insert(0, courseinputheadings[2])
    
    ### Course rating entry ###
    CourseRating = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseRating.insert(0, courseinputheadings[3])
    
    ### Course Bogey rating entry ###
    CourseBogRating = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseBogRating.insert(0, courseinputheadings[4])
    
    ### Course slope (Full course) entry ###
    CourseSlope = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseSlope.insert(0, courseinputheadings[5])
    
    ### Front Course rating entry ###
    CourseFPar = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseFPar.insert(0, courseinputheadings[6])
    
    ### Front course slope entry ###
    CourseFSlope = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseFSlope.insert(0, courseinputheadings[7])
    
    ### Back course rating entry ###
    CourseBPar = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseBPar.insert(0, courseinputheadings[8])
    
    ### Back course slope entry
    CourseBSlope = tk.Entry(wrapper_t2_2, width=inputwindowdict['Standard'], borderwidth=inputwindowdict['border'])
    CourseBSlope.insert(0, courseinputheadings[9])
    
    ### Position entry boxes ###
    CourseName.grid(row=1, column = 0)
    TeeCol_drop.grid(row=1, column = 1)
    CoursePar.grid(row=1, column = 2)
    CourseRating.grid(row=1, column = 3)
    CourseBogRating.grid(row=1, column = 4)
    CourseSlope.grid(row=1, column = 5)
    CourseFPar.grid(row=1, column = 6)
    CourseFSlope.grid(row=1, column = 7)
    CourseBPar.grid(row=1, column = 8)
    CourseBSlope.grid(row=1, column = 9)
    
    ### Bottons for data minipulation ###
    CourseSubmit = tk.Button(wrapper_t2_2, text='Submit', command=submitcourse)
    CourseSubmit.grid(row=3, column=0)
    
    courseimportdata = tk.Button(wrapper_t2_2, text='Import Course Info', command=courseimport) #data, dat_score, score_inf, dat_course, course_inf
    courseimportdata.grid(row=3, column=1)
    
    CourseRemove = tk.Button(wrapper_t2_2, text='Remove Course', command=course_entremove)
    CourseRemove.grid(row=3, column=9)
    
    # In[10]
    ##############################################################################
    ### Tab 3 - Data Analysis ###
    ##############################################################################
    ######################################
    #### Wrapper 1 Graph Output ####
    ######################################
    # Handles by plothcapdat routine !!!
    
    ######################################
    #### Wrapper 2 Display some simple stats and buttons ####
    ######################################
    UpdateGraph = tk.Button(wrapper_t3_2, text='UpdateG', command=None)
    UpdateGraph.grid(row=3, column=0)
    DoSomething = tk.Button(wrapper_t3_2, text='DoSomething', command=None) #data, dat_score, score_inf, dat_course, course_inf
    DoSomething.grid(row=3, column=1)
    
    
    # In[]
    #### Run main loop ####   
    root.mainloop()

if __name__ == '__main__':
    main()