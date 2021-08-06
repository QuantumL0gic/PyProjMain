#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 18:41:41 2021

@author: matexp
"""

import pandas as pd
import configparser
import os

# In[1]
##############################################################################
### Initialisation ###
##############################################################################
### Create paths and config files as necessary ###
#######################################
### Check paths exist or create them ###
def initialise(path, data, config_default, platform):
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
                       'hidx_data': 'handicapindexdata.csv',
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
        config.set('Data_File', 'hidx_data', defaultdict['hidx_data'])
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
    hidx_file = config.get('Data_File', 'hidx_data')
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
        course_dat = pd.read_csv(data+course_rat_file) #, index_col=[0,1])
    # Handicap Index data
    if not os.path.isfile(data+hidx_file):
        hidx_dat = pd.DataFrame(columns=['Date', 'Course', 'Tee', 'Direction', 'Score',
                                         'Net Score', 'Par', 'Rating', 'Slope', 'Differential', 'Handicap Index', 'PairingIdx', 'Inclusion'])
        hidx_dat.to_csv(data+hidx_file, header=True, index=False)
    else:
        hidx_dat = pd.read_csv(data+hidx_file)
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
    return score_file, hidx_file, course_rat_file, score_dat, course_dat, hidx_dat, direction_dat, tee_dat
