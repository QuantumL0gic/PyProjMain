#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 23:55:08 2021

World handicap system calculations of player handicap

This forms the necessary calculations to determine players handicap.

@author: matexp
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import configparser
import os
sys.path.append(os.path.abspath('/home/matexp/PyProj/hcap_calc/src'))
from hcapimporter import *


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

importfromfile = 'Y'
if importfromfile == 'Y':
    course_inf = data+'Course_Ratings_001.csv'
    score_inf = data+'GolfScores_001.csv'
# In[1]
##############################################################################
### Initialisation ###
##############################################################################
### Create paths and config files as necessary ###
#######################################
### Check paths exist or create them ###
if not os.path.exists(path):
    os.mkdir(path)
if not os.path.exists(data):
    os.mkdir(data)

### Set paths and parse config ###
configfile = data+config_default
config = configparser.ConfigParser()

### Check if configuration file exists or create one ###
if not os.path.isfile(configfile):
    defaultdict = {'data': data,
                   'score_data': 'hcapscoredata.csv',
                   'course_ratings': 'courseratingsdata.csv',
                   'Play_dir': 'playdirectionsinfo.csv',
                   'Tee_list': 'teelist.csv'}
    
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(configfile, "w")

    # Add content to the file
    config.add_section('File_Paths')
    config.set('File_Paths', 'data', defaultdict['data'])
    
    config.add_section('Data_File')
    config.set('Data_File', 'score_data', defaultdict['score_data'])
    #config.set('Data_File', 'course_ratings', defaultdict['course_ratings'])
    
    config.add_section('LIBRARIES')
    config.set('LIBRARIES', 'course_ratings', defaultdict['course_ratings'])
    config.set('LIBRARIES', 'Play_dir', defaultdict['Play_dir'])
    config.set('LIBRARIES', 'Tee_list', defaultdict['Tee_list'])
    config.write(cfgfile)
    cfgfile.close()
else:
    config.read(configfile)
    
### List all contents of config file (for testing) ###
if platform == 'Test':
    print("List all contents")
    for section in config.sections():
        print("Section: %s" % section)
        for options in config.options(section):
            print(
                "x %s:::%s:::%s"
                % (options, config.get(section, options), str(type(options)))
            )

### Get variable from configuration file ###
data = config.get('File_Paths', 'data')
score_file = config.get('Data_File', 'score_data')
course_rat_file = config.get('LIBRARIES', 'course_ratings')
play_dir_file = config.get('LIBRARIES', 'Play_dir')
tees_file = config.get('LIBRARIES', 'Tee_list')

### Next step:
### Check data files and libraries exist or create empty with headers and ask to be filled from file ###
# Score data
if not os.path.isfile(data+score_file):
    score_dat = pd.DataFrame(columns=['Date', 'Course', 'Tee', 'Direction', 'Score'])
    score_dat.to_csv(data+score_file, header=True, index=False)
else:
    score_dat = pd.read_csv(data+score_file)

# Course data and information for ratings
if not os.path.isfile(data+course_rat_file):
    course_dat = pd.DataFrame(columns=['Course', 'Tee', 'Par', 'Rating',
                                          'Bogey_Rating', 'Slope', 'Front_Par', 'Front_Slope', 'Back_Par', 'Back_Slope'])
    course_dat.to_csv(data+course_rat_file, header=True, index=False)
else:
    course_dat = pd.read_csv(data+course_rat_file)

# Direction of play
if not os.path.isfile(data+play_dir_file):
    directions_dict = {'Direction': ['Full', 'Front', 'Back']}
    direction_dat = pd.DataFrame.from_dict(directions_dict)
    direction_dat.to_csv(data+play_dir_file, header=True, index=False)
else:
    direction_dat = pd.read_csv(data+play_dir_file)

# List of Tees    
if not os.path.isfile(data+tees_file):
    tees_dict = {'Tee': ['White', 'Blue', 'Yellow', 'Red-Male', 'Red-Female']}
    tee_dat = pd.DataFrame.from_dict(tees_dict)
    tee_dat.to_csv(data+tees_file, header=True, index=False)
else:
    tee_dat = pd.read_csv(data+tees_file)

### Import data from external sources using hcapimorter script ###
if importfromfile == 'Y':
    score_dat = import_scores(data, score_dat, score_inf)
    course_dat = import_courseinfo(data, course_dat, course_inf)

