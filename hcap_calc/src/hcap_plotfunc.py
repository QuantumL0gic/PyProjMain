#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 00:02:28 2021

@author: matexp
"""
#import sys
#import os
#from pathlib import Path
##import matplotlib
import matplotlib.pyplot as plt
##matplotlib.use("TkAgg")
import pandas as pd
import numpy as np
from cycler import cycler

'''
GraphCols = ['#52595D', '#5E7D7E', '#E5E4E2', '#54C571', '#43C6DB', '#FFEF00', '#FF8040', '#C45AEC']

colcyc = cycler(sumit=GraphCols)
for i, c in zip(range(7), colcyc):
    print(c)
    print(c['sumit'])
#colcyc[7]
#sys.path.append(os.path.abspath('/home/matexp/PyProj/hcap_calc/src'))
#import init
#import hcapimporter as hi
#import hcapcalcs_main_v1_1 as hcalc

#test = dat_course.index.get_level_values(0).to_numpy()
#test = np.unique(test)
#test

home = str(Path.home())

platform = 'Test' # Test=Testing during development home=Home deirectory for user

if platform == 'Test':    
    path = home+'/PyProj/hcap_calc/'
elif platform == 'home':    
    path = home+'/Documents/'

data = path+'.hcap/'
config_default = 'hcap.conf'


def genhidx(dat_score_tmp):
    hidx_dat_tmp = hcalc.port_courserat(dat_score_tmp, dat_course, dat_direction) # Generate score differentials 
    hidx_dat_tmp = hcalc.calc_hidx_cidx(hidx_dat_tmp, dat_direction, calc_noninclusive) # Generate handicap index and course index info
    return hidx_dat_tmp


score_inf = path+'data/GolfScores_001.csv'
course_inf = path+'data/Course_Ratings_001.csv'

calc_noninclusive = 'Y' # provide a handicap index for non inclusive rounds within the handicap index calculations ie half rounds that have been paired.

file_score, file_hidx, file_course_rat, dat_score, dat_course, dat_hcap, dat_direction, dat_tee = init.initialise(path, data, config_default, platform)

dat_course = hi.import_courseinfo(data, dat_course, course_inf) # Import course data
dat_score_tmp = hi.import_scores(data, dat_score, score_inf) # Import score data

dat_hcap = genhidx(dat_score_tmp)

# In[0]
### Setup plotting function ###
wid = 18
hig = 6
appdpi = 600
#wid, hig = getplotsize()
var_Hidx = 1
var_Cidx =1
var_Diff = 1
var_Score = 1
var_NScore = 1
### Get columns of interest
col_list = []
if var_Hidx == 1:
    col_list.append('Handicap Index')
if var_Cidx == 1:
    col_list.append('CourseIdx')
if var_Diff == 1:
    col_list.append('Differential')
if var_Score == 1:
    col_list.append('Score')
if var_NScore == 1:
    col_list.append('Net Score')
#return col_list
#dat_hcap = dat_hcap

GraphCols = ['#52595D', '#5E7D7E', '#E5E4E2', '#54C571', '#43C6DB', '#FFEF00', '#FF8040', '#C45AEC']
#    Graph Cols:
#        Iron Gray,(axBG), Grayish Turquoise (figBG), Platinum (Axes/Text), Zombie Green (Line1), Blue Turquoise (Line2), Canary Yellow (Line3), Mango Orange (Line4), Tyrian Purple (Line5)
    '''

def plotfunc(dat_hcap, col_list, wid, hig, appdpi, GraphCols):
    ######################################
    ### Plotting and statistics functions ###
    ######################################
    ### Slice table only for included (selected scores) ###
    stats_df = dat_hcap[dat_hcap['Inclusion'] == 1]
    ### Set colours for graphing
    bgcol = GraphCols[0:2]
    #bgcol
    axistxtcols = GraphCols[2]
    statcols = GraphCols[3:8]
    #colours = ['#54C571', '#43C6DB', '#FFEF00', '#FF8040', '#C45AEC'] # Zombie Green, Blue Turquoise, Canary Yellow, Mango Orange, Tyrian Purple
    ### Plot out trends for selected columns ###
    # Set data for line plots
    xvals = stats_df['Date'].to_list()
    Dates = [date.strftime('%d/%m/%Y') for date in xvals]
    t = np.linspace(0,len(Dates), len(Dates))
    # Create figure for plotting
    with plt.rc_context({'axes.edgecolor': axistxtcols,
                         'axes.facecolor': bgcol[0],
                         'axes.prop_cycle': cycler('color',statcols),
                         'axes.titlecolor': axistxtcols,
                         'axes.labelcolor': axistxtcols,
                         'lines.linewidth': 2,
                         'lines.linestyle': '-',
                         'figure.facecolor': bgcol[1],
                         'xtick.color': axistxtcols,
                         'xtick.labelcolor': axistxtcols,
                         'ytick.color': axistxtcols,
                         'ytick.labelcolor': axistxtcols,
                         'text.color': axistxtcols
                         }):
        hidxdatfig = plt.figure(figsize=(wid, hig), dpi=appdpi)
        #hidxdatfig.set_facecolor(bgcol[1])
        # Create Line Plot axis
        ax1 = hidxdatfig.add_subplot(111)
        for i, col in enumerate(col_list):
            ax1.plot(t,stats_df[col].to_list(), label=col) #, color = statcols[i]
        # Setup axis limits, labels, legends easthetics etc
        #ax1.set_facecolor(bgcol[0])
        
        
        ax1.set_ylim([0, None])
        #ax1.set_xlim([min(xvals), max(xvals)])
        ax1.set_ylabel('Handicap Index')
        ax1.set_xlabel('Date')
        #tick_loc = ax1.get_xticks().tolist()
        #ax1.xaxis.set_major_locator(mticker.FixedLocator(tick_loc))
        ax1.set_xticks(t)
        ax1.set_xticklabels(Dates, rotation=45, ha='right')
        ax1.set_title('Handicap Index Variability')
        ax1.legend()
    
    
    #plt.show() #savefig('/home/matexp/Desktop/testplot.jpeg')
    #plt.close('all')
    
    return hidxdatfig
    
def basicstats(dat_hcap, col_list):
    ### Basic stats ###
    hcap_stats = dat_hcap[dat_hcap['Inclusion'] == 1]
    # Data tables
    stats_tmp = np.zeros((3,len(col_list)))
    for c, col in enumerate(col_list):
            statdat = hcap_stats[col].to_numpy()
            minval = np.amin(statdat)
            maxval = np.amax(statdat)
            meanval = round(np.mean(statdat), 1)
            stats_tmp[0,c] = minval
            stats_tmp[1,c] = maxval
            stats_tmp[2,c] = meanval
    
    basicstats_df = pd.DataFrame(data=stats_tmp, index=['Min', 'Max', 'Mean'], columns=col_list)
    basicstats_df = basicstats_df.round(decimals=1)
    '''
    # Note:
    # Score
    # !!! There are both front and back scores that may be included hence bias towards lower scores
    # Net Score - Which mitigates the bias by using normailised Course Index.
    '''
    return basicstats_df

#test1 = basicstats(dat_hcap, col_list)