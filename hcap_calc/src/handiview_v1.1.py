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
from tkinter import filedialog, messagebox, ttk, font
from ttkwidgets import CheckboxTreeview
#from pandastable import Table
import configparser
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mticker
from PIL import ImageTk, Image
from cycler import cycler
from itertools import cycle

sys.path.append(os.path.abspath('/home/matexp/PyProj/hcap_calc/src'))
import init
import hcapimporter as hi
import hcapcalcs_main_v1_1 as hcalc
from hcap_plotfunc import plotfunc, basicstats



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
icons = path+'icons/'


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
inclusionlist = []
scoreselected = []
courseselected = []
scoreidx = []
courseidx = []
course_entries = []
course_list = []
tee_list = dat_tee['Tee'].to_list()
direction_list = dat_direction['Direction'].to_list()

statcollist = []

### !!! Use for GUI esthetics ###
other_colours = ['#2e4053', '#9b59b6']

GraphCols = ['#52595D', '#5E7D7E', '#E5E4E2', '#54C571', '#43C6DB', '#FFEF00', '#FF8040', '#C45AEC']
Highlights = ['#c0392b', '#8e44ad', '#2980b9', '#16a085', '#f1c40f', '#f39c12', '#d35400']

fontfamilies = []
screenh = []
screenw = []
# In[2]:
##############################################################################
### Start the main loop for the application (need to put this into a class) ###
##############################################################################
def main():
##############################################################################
### Defined routines for GUI interactions ###
##############################################################################
### Tab 2 - Course Rating tab functionality ###
######################################
    ### Load data from Course Rating data table ###
    def load_course_data(course_info):
        # Create list of indexes in table
        tviewidx = []
        # Update table with entries from imported or manual entry
        clear_data_t2()
        
        cratdataview['column'] = list(course_info.columns)
        cratdataview['show'] = 'headings'
        for column in cratdataview['column']:
            cratdataview.heading(column, text=column, anchor='w')
            cratdataview.column(column, width=100, stretch=True, anchor='w')
        
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
    
    ### Remove entry from the course rating record table ###
    def course_entremove():
        course_tmp = dat_course
        course_tmp.drop(courseselected, inplace=True)
        load_course_data(course_tmp)
        # !!! Set rerun of differential calculation but preserve 'Inclusion' field 
        return None
    
    ### Fetch the index of the course selected in the view table ###
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
    ### Read the handicap index file ###
    def init_hidx_data():
        hidx_dat, calcIncs = genhidx(dat_score)
        load_course_data(dat_course)
        getcolofint()
        load_data(hidx_dat, calcIncs)
        return None
    
    ### Load data for handicap index file and generate table view ###
    def load_data(hidx_dat, calcIncs):
        # Create list of indexes in table
        print(calcIncs)
        tviewidx = []
        #calc_hidx_cidx
        #inclusion_state_df = 
        inclusion_state = hidx_dat['Inclusion'].to_numpy().tolist()
        
        # Setup hanidcap index table for viewing
        hidx_datview = hidx_dat.drop(['PairingIdx', 'Inclusion'], axis=1)
        hidx_dat['Date'] = pd.to_datetime(hidx_dat.Date, format='%d/%m/%Y', infer_datetime_format=True)
        
        clear_data()
        # Create inclusion column
        hidxviewcols = ['Include']
        cols = list(hidx_datview.columns)
        for col in cols:
            hidxviewcols.append(col)
        hidxdataview['column'] = hidxviewcols
        #hidxdataview['show'] = 'headings'
        for c, column in enumerate(hidxdataview['column']):
            hidxdataview.column('#'+str(c), width=100, stretch=True, anchor='w')
            hidxdataview.heading('#'+str(c), text=column, anchor='w')
            
        df_rows = hidx_datview.to_numpy().tolist()
        for i, row in enumerate(df_rows):
            if inclusion_state[i] == 1:
                tag = (tagslist[1])
            elif inclusion_state[i] == 0:
                tag = (tagslist[0])
            elif inclusion_state[i] == 2:
                tag = (tagslist[2])
            #tglist = calcIncs[:,i]
            '''
            inttags = calcIncs[i,:]
            strtags = [str(t) for t in inttags]
            #tags = calcIncs[i,:]
            print(strtags, np.shape(strtags))
            tags =list(strtags[:])
            print(tags)
            tags.insert(0,tag)
            print(tags)
            tags = tuple(tags)
            '''
            tags = (tag, showinctags[1])
            hidxdataview.insert('', 'end', iid=i, values = row, tags = tags) # !!! Use iid to select items from the database for deletion and minipulation
            tviewidx.append(i)
        global dat_score, dat_hcap, scoreidx, inclusionlist
        scoreidx = tviewidx
        dat_score = hidx_dat.iloc[:,0:5]
        dat_hcap = hidx_dat
        inclusionlist = calcIncs
        plothcapdat()
        return None
    ### Clear data from the table view ###
    def clear_data():
        hidxdataview.delete(*hidxdataview.get_children())
        return None
    
    ### Submit Entry for score data ###
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
            hidx_dat = hcalc.port_courserat(inscore, dat_course, dat_direction)
        except:
            inscore = pd.DataFrame(columns=scoreheaders)
            hidx_dat = pd.DataFrame(columns=dat_hcap.columns)
            tk.messagebox.showerror('Check Score Entry', 'Please check all entry fields and try again.')
        dat_hcap_tmp = dat_hcap
        dat_hcap_tmp = dat_hcap_tmp.append(hidx_dat)
        dat_hcap_tmp, calcIncs = hcalc.calc_hidx_cidx(dat_hcap_tmp, dat_direction, calc_noninclusive)
        load_data(dat_hcap_tmp, calcIncs)
        return None
    
    ### Remove score from records
    def score_entremove():
        hidx_dat = dat_hcap
        hidx_dat.drop(scoreselected, inplace=True)
        hidx_dat, calcIncs = hcalc.calc_hidx_cidx(hidx_dat, dat_direction, calc_noninclusive)
        load_data(hidx_dat, calcIncs)
        return None
    
    ### Fetch the index of a record in handicap index table ###
    def gethidxindex(event):
        rows = hidxdataview.selection()
        indexlist = []
        for row in rows:
            index = hidxdataview.index(row)
            indexlist.append(index)
        #iid = hidxdataview.identify(event.x, event.y)
        global scoreselected
        scoreselected = indexlist
        tog_calc_included(event)
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
            hidx_dat, calcIncs = genhidx(dat_score_tmp)
            load_data(hidx_dat, calcIncs)
        return None
    
    ### Toggle inclusion of score records in handicap index calculation ###
    def toggleinclusion(event):
        #row = hidxdataview.identify_row(event.y)
        row = hidxdataview.selection()
        index = hidxdataview.index(row)
        currenttag = hidxdataview.item(row, 'tags')[0]
        taglist = list(hidxdataview.item(row, 'tags'))
        notags = list(hidxdataview.item(row, 'tags'))
        notags.remove(currenttag)
        hidxdataview.item(row, tags=notags)
        if currenttag == tagslist[1]:
            newtag = tagslist[0]
            newinc = 0
        if currenttag == tagslist[2]:
            newtag = tagslist[0]
            newinc = 0
        if currenttag == tagslist[0]:
            newtag = tagslist[1]
            newinc = 1
        taglist[0] = newtag
        hidxdataview.item(row, tags=taglist)
        global dat_hcap
        dat_hcap.at[index,'Inclusion'] = newinc
        dat_hcap = dat_hcap
        return None
    
    ### Present included rows within the Handicap Index calculation ###
    def tog_calc_included(event):
        #row = hidxdataview.identify_row(event.y)
        # !!! Change !!!
        #hidxdataview.tag_configure('-9.0', background=TreeviewCols[0])
        #hidxdataview.configure(style='Treeview')
        ### Reset dats to None highlighted ###
        for l in range(len(inclusionlist)):
            taglist = list(hidxdataview.item(l, 'tags'))
            taglist[1] = showinctags[1]
            hidxdataview.item(l, tags=taglist)
        
        ### Get row of interest index ###
        row = hidxdataview.selection()
        index = hidxdataview.index(row)
        #currenttag = hidxdataview.item(row, 'tags')[index+1]
        ### Find which rows are included in the calcuations from the inclusion list ###
        # Only look at previous rows
        inclist = inclusionlist[index]#[:index,:]
        #hilightrows = np.where(inclist==index)
        #hilightrows = list(hilightrows[0])
        #print(list(hilightrows))
        # Get colour range
        col = cycle(Highlights)
        #hilightcol = next(col)
        for i in range(index):
            hilightcol = next(col)
        ### Set tag for inclusion list ###
        for r in inclist:#hilightrows:
            taglist = list(hidxdataview.item(r, 'tags'))
            taglist[1] = showinctags[0]
            hidxdataview.item(r, tags=taglist)
        hidxdataview.tag_configure(showinctags[0], background=hilightcol)
        hidxdataview.tag_configure(showinctags[1], background=TreeviewCols[0])
        '''
            tag = taglist[1]
        print(tag)
        if tag != '-9.0':
            print('Is tag')
            print(str(tag))
        else:
            print('is -9')
            print(str(tag))
        #col = cycler(colour=GraphCols)
        #for i, c in zip(range(index), col):
        #    colour = col[c]
        #    idcol = colour['colour']
        if tag != '-9.0':
            #hidxdataview.tag_configure('-9.0', background=TreeviewCols[0])
            hidxdataview.tag_configure(tag, background='black')
            hidxdataview.tag_configure('-9.0', background=TreeviewCols[0])
        else:
            hidxdataview.tag_configure('-9.0', background=TreeviewCols[0])
        '''
        return None
    ### Regenerate handicap and score indexes ###
    def regenhidx():
        dat_hcap_tmp, calcIncs = hcalc.calc_hidx_cidx(dat_hcap, dat_direction, calc_noninclusive)
        load_data(dat_hcap_tmp, calcIncs)
        return None
    ######################################
    ### Tab 3 - Analysis ###
    ######################################
    ### Get list of column values of interest from checkboxes ###
    def removelabels():
        wrapper_t3_2.children.clear()
        #for label in wrapper_t3_2.children.values():
        #    print(label)
        #    label.destroy()
        return None
    
    def getcolofint():
        col_list = []
        HSel = var_Hidx.get()
        CSel = var_Cidx.get()
        DiffSel = var_Diff.get()
        Sel = var_Score.get()
        NSSel = var_NetS.get()
        if HSel == 1:
            col_list.append('Handicap Index')
        if CSel == 1:
            col_list.append('CourseIdx')
        if DiffSel == 1:
            col_list.append('Differential')
        if Sel == 1:
            col_list.append('Score')
        if NSSel == 1:
            col_list.append('Net Score')
        global statcollist
        statcollist = col_list
        #plothcapdat()
        return col_list
    ### Plot function for Analysis view ###
    def plothcapdat():
        col_list = statcollist
        
        if len(dat_hcap) > 0:
            wid, hig = getplotsize()
            # Generate plot
            hidxdatfig = plotfunc(dat_hcap, col_list, wid, hig, appdpi, GraphCols)
            # Generate canvas and display plot
            line1 = FigureCanvasTkAgg(hidxdatfig, wrapper_t3_1)
            line1.draw()
            line1.get_tk_widget().place(relheight=1, relwidth=1) #pack(fill=tk.BOTH, expand=1)
            
            # Calculate some basic statistics and optimal handicap index            
            stats = basicstats(dat_hcap, col_list)
            opthidx, curhidx = hcalc.opt_hidx(dat_hcap)
            stats_display(stats, opthidx, curhidx)
        return None
    
    def stats_display(stats, opthidx, curhidx):
        ### Clear wrapper of all children ###
        labellist = []
        for label in wrapper_t3_2.children.values():
            labellist.append(label)
        for labels in labellist:
            print(labels)
            labels.destroy()
        
        ### Get list of columns ###
        #col_list = statcollist
        col_list = list(stats.columns)
        #pdid_list = list(stats.index.values)
        
        ### Create Labels for stats ###
        labopt = ttk.Label(wrapper_t3_2, text = 'Optimal Handicap Index')
        labcur = ttk.Label(wrapper_t3_2, text = 'Current Handicap Index')
        optstat = ttk.Label(wrapper_t3_2, text = str(opthidx))
        curstat = ttk.Label(wrapper_t3_2, text = str(curhidx))
        labopt.grid(row=0, column=0)
        labcur.grid(row=0, column=1)
        optstat.grid(row=1, column=0)
        curstat.grid(row=1, column=1)
        
        ### Create Treeview table for basic stats ###
        statsdataview = ttk.Treeview(wrapper_t3_2)#, style='T2.Treeview')
        if appscale == 2:
            xoffset = 0.35
        else:
            xoffset = 0.69
        statsdataview.place(relheight=0.9, relwidth = 0.30, rely = 0.01, relx = xoffset)#grid(row=0, column=2) #place(relheight=1, relwidth=1)
        # Setup columns for display
        statviewcols = ['Stat']
        for col in col_list:
            statviewcols.append(col)
        statsdataview['column'] = statviewcols
        statsdataview['show'] = 'headings'
        for col in statsdataview['column']:
            statsdataview.heading(col, text=col, anchor='w')
            statsdataview.column(col, width=75, stretch=True, anchor='w')
        # Populate rows with data
        df_rows = stats.reset_index(drop=False)
        df_rows = df_rows.to_numpy().tolist()
        for i, row in enumerate(df_rows):
            statsdataview.insert('', 'end', values = row)
        return None
    ######################################
    ### General functions ###
    ######################################
    ### Exit routine ###
    def on_close():
        close=messagebox.askyesno('Exit','Are you sure you want to exit?')
        if close:
            save=messagebox.askyesno('Save Tables','Would you like to save the current tables?')
            if save:
                state = savecacheddata()
                if state == True:
                    root.destroy()
            else:
                root.destroy()
            return None
    ### Save cached data in Treeview tables ###
    def savecacheddata():
        try:
            global dat_score, dat_course, dat_hcap
            dat_score.to_csv(data+file_score, header=True, index=False)
            dat_course.to_csv(data+file_course_rat, header=True, index=False)
            dat_hcap.to_csv(data+file_hidx, header=True, index=False)
            state = True
        except:
            state = False
        return state
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
            #clist_tmp = dat_course.index.get_level_values(0).to_numpy()
            #course_list = np.unique(clist_tmp)
        return None
    ### Get list of Tees ###
    #def gettees():
    #    global tee_list
    #    tee_list = dat_course['Tee'].unique()
    #    return None
    
    ### Generate handicap index table ###
    def genhidx(dat_score_tmp):
        hidx_dat_tmp = hcalc.port_courserat(dat_score_tmp, dat_course, dat_direction) # Generate score differentials 
        hidx_dat_tmp, calcIncs = hcalc.calc_hidx_cidx(hidx_dat_tmp, dat_direction, calc_noninclusive) # Generate handicap index and course index info
        return hidx_dat_tmp, calcIncs
    
    ### Set the course dropdown selection for entry based on available course in course rating table###
    def SetCoursedrop():
        if len(dat_course) > 0:
            #global Course_input
            Course_drop.config(values=tuple(course_list))
            #Course_drop = ttk.Combobox(wrapper2, value=course_list)
            #Course_drop.grid(row=2, column = 1)
            #Course_drop.current(scoreinputheadings[1])
        return None
    
    ### Set the tee dropdown selection based on Tees available for the course in course dropdown selection ###
    def SetTeeDrop(e):
        Tee_list_tmp = dat_course.loc[dat_course['Course'] == Course_drop.get()]
        Tee_list_tmp = Tee_list_tmp['Tee'].to_list()
        if len(Tee_list_tmp) > 0:
            Tee_drop.config(values=tuple(Tee_list_tmp))
        else:
            Tee_drop.config(values=None)
            Tee_drop.set(scoreinputheadings[2])
        return None
    
    ### generate the size of the plot based on app size and dpi (matplot lib only uses inches!)###
    def getplotsize():
        ploth_pix = round(appwinheight/2)
        ploth_inch = ploth_pix/appdpi
        plotw_inch = ploth_inch*3 #/9)*10
        
        return plotw_inch, ploth_inch
    
    # In[3]
    
    
    
    # In[4]
    ##############################################################################
    ### Easthetics ###
    ##############################################################################
    ### Constants and easthetic params for gui ###
    '''
    # Frame Colour
    FrameCols = ['#2C3539', '#52595D', '#551606'] # Gunmetal, Iron Gray, Blood Night
    # Treeview Table Colour
    TreeviewCols = ['#52595D', '#29465B'] # Iron Gray, Dark Blue Grey
    # Button, entry, combo and tick boxes
    BoxButtonCols = ['#52595D', '#29465B', '#5E7D7E'] # Iron Gray, Dark Blue Grey, Grayish Turquoise
    # Graph output colours
    GraphCols = ['#5E7D7E', '#E5E4E2', '#54C571', '#43C6DB', '#FFEF00', '#FF8040', '#C45AEC']
    '''
    #Graph Cols:
    #    Grayish Turquoise (BG), Platinum (Axes/Text), Zombie Green (Line1), Blue Turquoise (Line2), Canary Yellow (Line3), Mango Orange (Line4), Tyrian Purple (Line5)
    '''
    # Font colours
    FontCols = ['#E5E4E2'] # Platinum
    '''
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
    
    ### For window exit ###
    root.protocol('WM_DELETE_WINDOW',on_close)
    #root.geometry(windowdim)
    
    screenheight = root.winfo_screenheight()
    screenwidth = root.winfo_screenwidth()
    #screenheight = 1080
    #screenwidth = 1920
    if screenheight > 1080:
        appscale = 2
    else:
        appscale = 1
    
    appwinheight = round(screenheight/appscale)
    appwinwidth = round(screenwidth/appscale)
    appdpi = root.winfo_fpixels('1i')
    
    appgeom = str(appwinwidth)+'x'+str(appwinheight)
    
    root.geometry(appgeom)
    
#    global screenh, screenw
#    screenh = screenheight
#    screenw = screenwidth
    #mainfont = font.nametofont('TkDefaultFont')
    #mainfont.configure(size='72')
    #root.option_add('*Font', mainfont)
    ### Add tab control and tabs ###
    tabControl = ttk.Notebook(root) #, style='N1.TNotebook')
    tab1 = ttk.Frame(tabControl) #, style='F1.TFrame')
    tab2 = ttk.Frame(tabControl) #, style='F1.TFrame')
    tab3 = ttk.Frame(tabControl) #, style='F1.TFrame')
    
    tabControl.add(tab1, text='Handicap Index')
    tabControl.add(tab2, text='Course Ratings')
    tabControl.add(tab3, text='Analysis')
    
    tabControl.pack(expand=1, fill='both')
    ######################################
    ### Add internal tab wrappers for input and viewing data ###
    ######################################
    ### Tab 1 - Handicap Index View and score submition/import ###
    wrapper1 = ttk.Labelframe(tab1, text='Handicap Viewer')#, style='LF1.TLabelframe') #.LabelFrame(tab1, text='Handicap Viewer')
    wrapper2 = ttk.Labelframe(tab1, text='Submit Score')#, style='LF1.TLabelframe') # tk.LabelFrame(tab1, text='Submit Score')
    #wrapper3 = tk.LabelFrame(tab1, text='Analysis Views')
    
    wrapper1.place(relheight=0.7, relwidth = 0.99, rely = 0.01, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    wrapper2.place(relheight=0.27, relwidth = 0.99, rely = 0.72, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    #wrapper3.pack(fill='both', expand='yes', padx=20, pady=10)
    
    
    ### Tab 2 - Course information and submition/import ###
    wrapper_t2_1 = ttk.Labelframe(tab2, text='Course Rating Viewer')#, style='LF1.TLabelframe')
    wrapper_t2_2 = ttk.Labelframe(tab2, text='Submit Course Information')#, style='LF1.TLabelframe')
    
    wrapper_t2_1.place(relheight=0.7, relwidth = 0.99, rely = 0.01, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    wrapper_t2_2.place(relheight=0.27, relwidth = 0.99, rely = 0.72, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    
    ### Tab 3 - View analysis and graphs ###
    wrapper_t3_1 = ttk.Labelframe(tab3, text='Graph Analysis')#, style='LF1.TLabelframe')
    wrapper_t3_2 = ttk.Labelframe(tab3, text='Statistical Analysis')#, style='LF1.TLabelframe')
    wrapper_t3_3 = ttk.Labelframe(tab3, text='Analysis and Statitics Tools')#, style='LF1.TLabelframe')
    
    wrapper_t3_1.place(relheight=0.6, relwidth = 0.99, rely = 0.01, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    wrapper_t3_2.place(relheight=0.185, relwidth = 0.99, rely = 0.62, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    wrapper_t3_3.place(relheight=0.185, relwidth = 0.99, rely = 0.805, relx = 0.005) # pack(fill='both', expand='yes', padx=20, pady=10)
    # In[6]
    ##############################################################################
    ### Tab 1 - Handicap Index view, score submition, importing of data  ###
    ##############################################################################
    ### Wrapper 1 Data view and information ###
    ######################################
    ### Create Score/Handicap index Treeview table ###
    hidxdataview = ttk.Treeview(wrapper1)#, style='T1.Treeview')
    hidxdataview.place(relheight=1, relwidth=1)
    
    ### Add controls, scroll bars etc to treeview table ###
    dataviewscrolly = ttk.Scrollbar(wrapper1, orient='vertical', command=hidxdataview.yview)
    dataviewscrollx = ttk.Scrollbar(wrapper1, orient='horizontal', command=hidxdataview.xview)
    hidxdataview.configure(xscrollcommand=dataviewscrollx.set, yscrollcommand=dataviewscrolly.set)
    dataviewscrollx.pack(side='bottom', fill='x')
    dataviewscrolly.pack(side='right', fill='y')
    
    ### Add tag configuration to show images (for inclusion status) ###
    tagslist = ['Dismissed', 'Included', 'Waiting']
    showinctags = ['Inc', 'None']
    
    # Import images
    incimage = ImageTk.PhotoImage(Image.open(icons+'starred.png'))
    waitimage = ImageTk.PhotoImage(Image.open(icons+'semi-starred-rtl.png'))
    nonincimage = ImageTk.PhotoImage(Image.open(icons+'non-starred.png'))
    
    hidxdataview.tag_configure(tagslist[1], image=incimage)
    hidxdataview.tag_configure(tagslist[0], image=nonincimage)
    hidxdataview.tag_configure(tagslist[2], image=waitimage)
    
    
    ### Load handicap data ###
    #init_hidx_data()#load_data(dat_hcap)
    
    ### Bindings for treview table ###
    hidxdataview.bind('<ButtonRelease-1>', gethidxindex)
    hidxdataview.bind('<Double-1>', toggleinclusion)
    # In[7]
    ######################################
    #### Wrapper 2 Data submition ####
    ######################################
    ### Date input ###
    Date_input = ttk.Entry(wrapper2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
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
    Score_input = ttk.Entry(wrapper2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    Score_input.insert(0, scoreinputheadings[4])
    
    ### Position input widgets ###
    Date_input.grid(row=2, column = 0)
    Course_drop.grid(row=2, column = 1)
    Tee_drop.grid(row=2, column = 2)
    Direction_drop.grid(row=2, column = 3)
    Score_input.grid(row=2, column = 4)
    
    ### Bottons for submiting and importing data ###
    submitdrop = ttk.Button(wrapper2, text='Submit Score', command=submitdrop)
    submitdrop.grid(row=3, column=0)
    
    importdata = ttk.Button(wrapper2, text='Import Scores ff', command=scoreimport) #data, dat_score, score_inf, dat_course, course_inf
    importdata.grid(row=3, column=1)
    
    removescore = ttk.Button(wrapper2, text='Remove Entry', command=score_entremove) #data, dat_score, score_inf, dat_course, course_inf
    removescore.grid(row=3, column=4)
    
    Recalc = ttk.Button(wrapper2, text='Regenerate Scores', command=regenhidx) #data, dat_score, score_inf, dat_course, course_inf
    Recalc.grid(row=5, column=1)

    ### Bindings for drop down selection ###
    Course_drop.bind('<<ComboboxSelected>>', SetTeeDrop)
    
    # In[8]
    ##############################################################################
    ### Tab 2 - Course Rating view, course information submition, importing of data  ###
    ##############################################################################
    ### Wrapper 1 Course rating data view and information ###
    #####################################
    ### Create Course Treeview table ###
    cratdataview = ttk.Treeview(wrapper_t2_1, style='T2.Treeview')
    cratdataview.place(relheight=1, relwidth=1)
    
    ### Add controls, scroll bars etc to treeview table ###
    cratdatascrolly = ttk.Scrollbar(wrapper_t2_1, orient='vertical', command=cratdataview.yview)
    cratdatascrollx = ttk.Scrollbar(wrapper_t2_1, orient='horizontal', command=cratdataview.xview)
    cratdataview.configure(xscrollcommand=cratdatascrollx.set, yscrollcommand=cratdatascrolly.set)
    cratdatascrollx.pack(side='bottom', fill='x')
    cratdatascrolly.pack(side='right', fill='y')
    
    ### Set style for table ###
    #coursestyle = ttk.Style(cratdataview)
    #coursestyle.configure('T2.Treeview', rowheight = 25) # Images are 32 pixels
    
    ### Load course data from initialisation ###
    load_course_data(dat_course)
    
    ### Bind treeview selection for removal/editing of entry ###
    cratdataview.bind('<ButtonRelease-1>', getcratindex)
    # In[9]
    ######################################
    #### Wrapper 2 Data submition ####
    ######################################
    ### Course Name entry ###
    CourseName = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseName.insert(0, courseinputheadings[0])
    
    ### Tee Colour entry###
    TeeCol_drop = ttk.Combobox(wrapper_t2_2, value=tuple(tee_list))
    TeeCol_drop.set(scoreinputheadings[2]) #current
    
    ### Course Par entry ###
    CoursePar = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CoursePar.insert(0, courseinputheadings[2])
    
    ### Course rating entry ###
    CourseRating = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseRating.insert(0, courseinputheadings[3])
    
    ### Course Bogey rating entry ###
    CourseBogRating = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseBogRating.insert(0, courseinputheadings[4])
    
    ### Course slope (Full course) entry ###
    CourseSlope = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseSlope.insert(0, courseinputheadings[5])
    
    ### Front Course rating entry ###
    CourseFPar = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseFPar.insert(0, courseinputheadings[6])
    
    ### Front course slope entry ###
    CourseFSlope = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseFSlope.insert(0, courseinputheadings[7])
    
    ### Back course rating entry ###
    CourseBPar = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
    CourseBPar.insert(0, courseinputheadings[8])
    
    ### Back course slope entry
    CourseBSlope = ttk.Entry(wrapper_t2_2, width=inputwindowdict['Standard']) #, borderwidth=inputwindowdict['border'])
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
    CourseSubmit = ttk.Button(wrapper_t2_2, text='Submit', command=submitcourse)
    CourseSubmit.grid(row=3, column=0)
    
    courseimportdata = ttk.Button(wrapper_t2_2, text='Import Course Info', command=courseimport) #data, dat_score, score_inf, dat_course, course_inf
    courseimportdata.grid(row=3, column=1)
    
    CourseRemove = ttk.Button(wrapper_t2_2, text='Remove Course', command=course_entremove)
    CourseRemove.grid(row=3, column=9)
    
    # In[10]
    ##############################################################################
    ### Tab 3 - Data Analysis ###
    ##############################################################################
    ######################################
    #### Wrapper 1 Graph Output ####
    ######################################
    # Handled by plothcapdat routine !!! called on load_data
    
    ######################################
    #### Wrapper 2 Statistics figures display ####
    ######################################
    #label = ttk.Label(wrapper_t3_3, text = col_list[col])
    
    ######################################
    #### Wrapper 3 Select stats if interest and run analysis ###
    ######################################
    ### Buttons for regraphing ###
    UpdateGraph = ttk.Button(wrapper_t3_3, text='Update Graph', command=plothcapdat)
    UpdateGraph.grid(row=3, column=0)
    DoSomething = ttk.Button(wrapper_t3_3, text='RemoveLabels', command=removelabels) #data, dat_score, score_inf, dat_course, course_inf
    DoSomething.grid(row=3, column=1)
    
    XaxisSelectLab = ttk.Label(wrapper_t3_3, text='Plot Statistics')
    XaxisSelectLab.grid(row=4, column=0)
    
    #StatSelectLab = tk.Label(wrapper_t3_3, text='Plot Statistics')
    #StatSelectLab.grid(row=4, column=0)
    ### Create checkboxs for stats to be shown in statistics calculations ###
    # Get images for checkbutton
    #on_check = ImageTk.PhotoImage(Image.open(data+'checkbox-checked.png'))
    #on_check
    #off_check = ImageTk.PhotoImage(Image.open(data+'dialog-error.png'))
    
    var_Hidx = tk.IntVar(value=1)
    var_Cidx = tk.IntVar(value=1)
    var_Diff = tk.IntVar(value=1)
    var_Score = tk.IntVar(value=1)
    var_NetS = tk.IntVar(value=1)
    check_Hidx = ttk.Checkbutton(wrapper_t3_3, text='Handicap Index', variable=var_Hidx, onvalue=1, offvalue=0, command=getcolofint)
    check_Cidx = ttk.Checkbutton(wrapper_t3_3, text='Course Index', variable=var_Cidx, onvalue=1, offvalue=0, command=getcolofint)
    check_Diff = ttk.Checkbutton(wrapper_t3_3, text='Score Differential', variable=var_Diff, onvalue=1, offvalue=0, command=getcolofint)
    check_Score = ttk.Checkbutton(wrapper_t3_3, text='Gross Score', variable=var_Score, onvalue=1, offvalue=0, command=getcolofint)
    check_NetS = ttk.Checkbutton(wrapper_t3_3, text='Net Score', variable=var_NetS, onvalue=1, offvalue=0, command=getcolofint)

    check_Hidx.grid(row=5,column=0)
    check_Cidx.grid(row=5,column=1)
    check_Diff.grid(row=5,column=2)
    check_Score.grid(row=5,column=3)
    check_NetS.grid(row=5,column=4)

    # In[11]
    ##############################################################################
    ### Loading of initial data from saved files ###
    ##############################################################################
    init_hidx_data()
    
    # In[12]
    ##############################################################################
    ### Configure style and themes ###
    ##############################################################################
    # Frame Colour
    FrameCols = ['#2C3539', '#52595D', '#551606'] # Gunmetal, Iron Gray, Blood Night
    # Treeview Table Colour
    TreeviewCols = ['#52595D', '#29465B'] # Iron Gray, Dark Blue Grey
    # Button, entry, combo and tick boxes
    BoxButtonCols = ['#52595D', '#29465B', '#5E7D7E'] # Iron Gray, Dark Blue Grey, Grayish Turquoise
    # Graph output colours
    #GraphCols = ['#52595D', '#5E7D7E', '#E5E4E2', '#54C571', '#43C6DB', '#FFEF00', '#FF8040', '#C45AEC']
    '''
    Graph Cols:
        Iron Gray,(BG), Grayish Turquoise (BG), Platinum (Axes/Text), Zombie Green (Line1), Blue Turquoise (Line2), Canary Yellow (Line3), Mango Orange (Line4), Tyrian Purple (Line5)
    '''
    # Font colours
    FontCols = ['#E5E4E2'] # Platinum

    fontfams = font.families()
    
    mainfont = font.Font(family='malayalam',size=8)
    
    global fontfamilies
    fontfamilies = fontfams
    #mainfont = font.nametofont('TkDefaultFont')
    #mainfont.configure(size=100)
    #FontTypesHelv = ('fixed', 50, 'bold')
    #FontTypes[0]
    b_reliefs = ["flat", "raised", "sunken", "ridge", "solid", "groove"]
    
    #on_check = ImageTk.PhotoImage(Image.open(data+'checkbox-checked.png'))
    #on_check
    #off_check = ImageTk.PhotoImage(Image.open(data+'dialog-error.png'))
    ##################################
    ### Use Theme ###
    ##################################
    #
    style = ttk.Style()
    #style.theme_use("alt")
    ### Set theme ###
    style.theme_create( "DarkMain",
                   parent="alt", # alt, clam, default
                   settings={"TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0],
                                                         "background": FrameCols[0],
                                                         "foreground": FontCols[0],
                                                         "font" : mainfont
                                                         } },
                             "TNotebook.Tab": {"configure": {"padding": [5, 1],
                                                             "font" : mainfont,
                                                             "background": FrameCols[1],
                                                             "foreground": FontCols[0]},
                                               "map":       {"background": [("selected", BoxButtonCols[2])],
                                                             "foreground": [("selected", FontCols[0])],
                                                             "expand": [("selected", [1, 1, 1, 0])] } },
                             "Treeview": {"configure": {"rowheight": 32,
                                                        "font" : mainfont,
                                                        "background": TreeviewCols[0],
                                                        "foreground": FontCols[0],
                                                        "fieldbackground": TreeviewCols[0]},
                                          "map": {"background": [("selected", BoxButtonCols[2])]}},
                             "TButton": {"configure": {"padding": [5, 5],
                                                       "font" : mainfont,
                                                       "background": BoxButtonCols[0],
                                                       "foreground": FontCols[0],
                                                       "borderwidth": 3,
                                                       "bordercolor": FontCols[0],
                                                       "relief": b_reliefs[1]},
                                         "map": {"background": [('disabled',FrameCols[2]), ('active',BoxButtonCols[2])],
                                                 "relief": [('pressed', '!disabled', 'sunken')]}},
                             "TFrame": {"configure": {"font": mainfont,
                                                      "background": FrameCols[0],
                                                      "foreground": FontCols[0]}},
                             "TLabelframe": {"configure": {"font": mainfont,
                                                      "background": FrameCols[0],
                                                      "foreground": FrameCols[0]}}, #FontCols[0]
                             "TLabelframe.Label": {"configure": {"font": mainfont,
                                                                 'padding': [30, 30],
                                                                 "background": FrameCols[1],
                                                                 "foreground": FontCols[0]}}, #FontCols[0]
                             "TLabel": {"configure": {"padding": [40,20],
                                                      "font": mainfont,
                                                      "background": FrameCols[1],
                                                      "foreground": FontCols[0],
                                                      "borderwidth": 2,
                                                      "bordercolor": FontCols[0],
                                                      "relief": b_reliefs[2]}}, #"borderwidth": 4,
                             "TCheckbutton": {"configure": {"padding": [20, 20],
                                                            "font": mainfont,
                                                            "background": FrameCols[1],
                                                            "foreground": FontCols[0],
                                                            "borderwidth": 2,
                                                            "relief": b_reliefs[3]},
                                              "map": {"background": [('disabled',FrameCols[2]), ('selected',BoxButtonCols[2])],
                                                      "foreground": [('disabled',FontCols[0]), ('selected',FontCols[0])]}}
                             }
                   )
    style.theme_use("DarkMain")
    ###################################
    ### General Items ###
    ###################################
    # Frame
    #mainTheme = ttk.Style(root)
    #mainTheme.configure('F1.TFrame', font=FontTypes[0], background=FrameCols[0], foreground = FontCols[0])
    
    # Notebook
    #notebookstyle = ttk.Style(root)
    #mainTheme.configure('N1.TNotebook', font=FontTypes[0], background=FrameCols[0], foreground = FontCols[0])
    
    # Label Frame
    #labelframestyle = ttk.Style(root)
    #mainTheme.configure('LF1.TLabelframe', font=FontTypes[0], background=FrameCols[0], foreground = FontCols[0])
    # Scrollbars
    
    # Entry
    
    # Combobox
    
    # Button
    
    ###################################
    ### Tab 1 ###
    ###################################
    ### Set style treeview Score and Hcap table ###
    #scorestyle = ttk.Style(hidxdataview)
    #scorestyle.configure('T1.Treeview', rowheight = 32, font=FontTypes[0], background=TreeviewCols[0], foreground = FontCols[0]) # Images are 32 pixels
    
    ###################################
    ### Tab 2 ### 
    ###################################    
    ### Set style for table ###
    coursestyle = ttk.Style(cratdataview)
    coursestyle.configure('T2.Treeview',
                          rowheight = 25,
                          font=mainfont,
                          background=TreeviewCols[1],
                          foreground = FontCols[0],
                          fieldbackground = TreeviewCols[1]) # Images are 32 pixels
    
    ###################################
    ### Tab 3 ### 
    ###################################    
    # Label
    
    # Checkbuttons
    
    # In[]
    #### Run main loop ####   
    root.mainloop()

if __name__ == '__main__':
    main()
    
x = np.where(inclusionlist==6)
print(list(x[0]))
