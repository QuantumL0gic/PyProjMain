#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 16:00:53 2021

Import data from file (csv)

@author: matexp
"""

import pandas as pd
#import numpy as np
#from pathlib import Path
#import configparser
#import os

# In[1]
##############################################################################
### Load csv data files and update with imported data from file ###
##############################################################################
def import_scores(datapath, score_dat, score_inf):
    s_cols_dict = {'s_dat_cols': ['Date', 'Course', 'Tee', 'Direction', 'Score'],
               's_cols': ['Date', 'Course', 'Tee', 'Front/Back', 'Score']}
    score_tmp = pd.DataFrame(columns=s_cols_dict['s_dat_cols'])
    scores = pd.read_csv(score_inf)
    for name in range(len(s_cols_dict['s_dat_cols'])):
        xi = s_cols_dict['s_dat_cols'][name]
        yi = s_cols_dict['s_cols'][name]
        score_tmp[xi] = scores[yi]
    score_dat = score_dat.append(score_tmp)
    return score_dat

def import_courseinfo(datapath, course_dat, course_inf):
    course_dat.reset_index()
    c_cols_dict = { 'c_dat_cols': ['Course', 'Tee', 'Par', 'Rating',
                                          'Bogey_Rating', 'Slope', 'Front_Par', 'Front_Slope', 'Back_Par', 'Back_Slope'],
                 'c_rat_cols': ['Course Name', 'Tee', 'Par', 'Course Rating',
                                          'Bogey Rating', 'Slope Rating', 'Front (Par)', 'Front (Slope)', 'Back (Par)', 'Back (Slope)']}
    course_tmp = pd.DataFrame(columns=c_cols_dict['c_dat_cols'])
    course_ratings = pd.read_csv(course_inf)
    for name in range(len(c_cols_dict['c_dat_cols'])):
        xi = c_cols_dict['c_dat_cols'][name]
        yi = c_cols_dict['c_rat_cols'][name]
        course_tmp[xi] = course_ratings[yi]
    course_dat = course_dat.append(course_tmp)
    course_dat.sort_values('Course', inplace=True)
    return course_dat