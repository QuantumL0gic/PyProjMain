#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 16:00:53 2021

Import data from file (csv)

@author: matexp
"""

import pandas as pd
import numpy as np
from pathlib import Path
import configparser
import os



# In[0]
##############################################################################
### Setup directories and input arguments ###
##############################################################################
home = str(Path.home())

platform = 'Test' # Test=Testing during development home=Home deirectory for user

if platform == 'Test':    
    path = home+'/PyProj/hcap_calc/'
    data = path+'data/'
    config_default = 'hcap.conf'
elif platform == 'home':    
    path = home+'/Documents/'
    data = path+'data/'
    config_default = 'hcap.conf'

importfromfile = 'N'

course_inf = data+'Course_Ratings_001.csv'
score_inf = data+'GolfScores_001.csv'

# In[1]
##############################################################################
### File header Mappings for import ###
##############################################################################
s_cols_dict = {'s_dat_cols': ['Date', 'Course', 'Tee', 'Direction', 'Score'],
               's_cols': ['Date', 'Course', 'Tee', 'Front/Back', 'Score']}

c_cols_dict = { 'c_dat_cols': ['Course', 'Tee', 'Par', 'Rating',
                                          'Bogey_Rating', 'Slope', 'Front_Par', 'Front_Slope', 'Back_Par', 'Back_Slope'],
                 'c_rat_cols': ['Course Name', 'Tee', 'Par', 'Course Rating',
                                          'Bogey Rating', 'Slope Rating', 'Front (Par)', 'Front (Slope)', 'Back (Par)', 'Back (Slope)']}

# In[1]
##############################################################################
### Load csv data files and update with imported data from file ###
##############################################################################

score_dat = pd.read_csv(data+'hcapscoredata.csv')
course_dat = pd.read_csv(data+'courseratingsdata.csv')

scores = pd.read_csv(score_inf)
for name in range(len(s_cols_dict['c_dat_cols'])):
    xi = s_cols_dict['s_dat_cols'][name]
    yi = s_cols_dict['s_cols'][name]
    score_dat[xi] = scores[yi]

course_ratings = pd.read_csv(course_inf)
for name in range(len(c_cols_dict['c_dat_cols'])):
    xi = c_cols_dict['c_dat_cols'][name]
    yi = c_cols_dict['c_rat_cols'][name]
    course_dat[xi] = course_ratings[yi]