#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 16:29:12 2020

Read in ods format file and create csv for future needs


@author: matexp
"""

import configparser
import pandas as pd
import io
import os


from pathlib import Path
home = str(Path.home())

path = home+'/Documents/'
maindoc = 'RTWFlightFSX.ods'
csv_doc = 'RTWFlightFSX.csv'
config_default = 'fsxgui.conf'
current = os.getcwd()
#os.chdir(home+'Documents')
#fsxdata = pd.read_excel(path+maindoc, sheet_name='FlightsFInal', skiprows=2, engine='odf', na_values=" ",)

fsxdf = pd.read_csv(path+csv_doc, skiprows=1)

fsxdf.to_csv(path+'FSXdata'+'.csv', index=False)

defaultdict = {'mainpath': home+'/Documents/',
               'flightdata': home+'/Documents/',
               'flightvideo': home+'/Documents/',
               'fsxdatafile': 'FSX_DATA.csv',
               'fsxaircraftlib': 'FSX_CRAFT_LIB.csv',
               'fsxairportlib': 'FSX_PORT_LIB.csv'}

#fsxconf = pd.DataFrame(defaultdict)
#fsxconf.to_csv(path+config_default)

    
configfile = path+config_default # +'.ini'
if not os.path.isfile(configfile):
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(configfile, "w")

    # Add content to the file
    Config = configparser.ConfigParser()
    Config.add_section('File_Paths')
    Config.set('File_Paths', 'mainpath', defaultdict['mainpath'])
    Config.set('File_Paths', 'flightdata', defaultdict['flightdata'])
    Config.set('File_Paths', 'flightvideo', defaultdict['flightvideo'])
    
    Config.add_section('File_Names')
    Config.set('File_Names', 'fsxdatafile', defaultdict['fsxdatafile'])
    Config.set('File_Names', 'fsxaircraftlib', defaultdict['fsxaircraftlib'])
    Config.set('File_Names', 'fsxairportlib', defaultdict['fsxairportlib'])
    Config.write(cfgfile)
    cfgfile.close()


#f = open(configfile_name, 'r')
#sample_config = f.read()
config = configparser.ConfigParser()
config.read(configfile)
config.sections()

#config = configparser.RawConfigParser(allow_no_value=True)
#config.read(sample_config)
    

# Load the configuration file

# List all contents
print("List all contents")
for section in config.sections():
    print("Section: %s" % section)
    for options in config.options(section):
        print(
            "x %s:::%s:::%s"
            % (options, config.get(section, options), str(type(options)))
        )

# Print some contents
#print("\nPrint some contents")
#print(config.get("other", "use_anonymous"))  # Just get the value
#print(config.getboolean("other", "use_anonymous"))  # You know the datatype?

