#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 23:55:08 2021

World handicap system calculations of player handicap

This forms the necessary calculations to determine players handicap.

@author: matexp
"""
import pandas as pd
    
neutral = 113
# In[2]
##############################################################################
### Calculate handicap differentials from scores ###
##############################################################################
### Create table of results from score and course info ###
######################################
# Column names
def port_courserat(dat_score, dat_course, dat_direction):
    headers = list(dat_score.columns)
    headers.extend(['Par', 'Rating', 'Slope', 'Differential', 'Handicap Index', 'PairingIdx', 'Inclusion']) #, 'HandicapIdx_inclusion'
    # Create initial table
    dat_hcap = pd.DataFrame(columns=headers)
    # Populate table with score info
    dat_hcap = dat_hcap.append(dat_score)
    dat_hcap['Date'] = pd.to_datetime(dat_hcap.Date, format='%d/%m/%Y', infer_datetime_format=True)
    dat_hcap = dat_hcap.sort_values('Date', ascending=True)
    dat_hcap.reset_index(inplace=True, drop=True)
    #dat_hcap.set_index('Date', inplace=True)
    
    # Set multi-indexing for info lookups
    # !!! Need to fix so index is not called every time otherwise error occurs
    if len(dat_course.index.names) != 2:
        dat_course.set_index(['Course', 'Tee'], inplace = True)     
    
    # Populate with course info
    #for date in dat_hcap['Date']:
    #    print(date)
    #hcap_index = dat_hcap.index.values
        
    for date in range(len(dat_hcap['Date'])): #dat_hcap['Date']
        if dat_hcap.iloc[date,3] == dat_direction.iloc[0,0]:
            dat_hcap.iloc[date,5] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Par']
            dat_hcap.iloc[date,6] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Rating']
            dat_hcap.iloc[date,7] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Slope']
        elif dat_hcap.iloc[date,3] == dat_direction.iloc[1,0]:
            dat_hcap.iloc[date,5] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Front_Par']
            dat_hcap.iloc[date,6] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Front_Par']
            dat_hcap.iloc[date,7] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Front_Slope']
        elif dat_hcap.iloc[date,3] == dat_direction.iloc[2,0]:
            dat_hcap.iloc[date,5] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Back_Par']
            dat_hcap.iloc[date,6] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Back_Par']
            dat_hcap.iloc[date,7] = dat_course.loc[tuple([dat_hcap.iloc[date,1],dat_hcap.iloc[date,2]]), 'Back_Slope']
    
    dat_hcap['Handicap Index'] = 0.0
    dat_hcap['PairingIdx'] = 0
    #dat_hcap['HandicapIdx_inclusion'] = (0)
    dat_hcap['Inclusion'] = 1
    ######################################
    ### Calculate score differentials ###
    ######################################
    #print(dat_hcap.dtypes)
    dat_hcap = dat_hcap.astype({'Score': 'float',
                                'Par': 'float',
                                'Rating': 'float',
                                'Slope': 'float',
                                'Differential': 'float',
                                'Handicap Index': 'float',
                                'PairingIdx': 'int',
                                'Inclusion': 'int'})
    #dat_hcap['Differential'] = (((dat_hcap['Score']-dat_hcap['Rating'])*neutral)/dat_hcap['Slope'])
    
    return dat_hcap

# In[3]
##############################################################################
### Calculate handicap Index from differentials using WHS methodology ###
##############################################################################
### Slice table for included differentials in calculations ###
def calc_hidx_cidx(dat_hcap, dat_direction, calc_noninclusive):
    ### Reformat dat_hcap and sort by descending date ###
    dat_hcap['Date'] = pd.to_datetime(dat_hcap.Date, format='%d/%m/%Y', infer_datetime_format=True)
    dat_hcap = dat_hcap.sort_values('Date', ascending=True)
    dat_hcap.reset_index(inplace=True, drop=True)
    
    ### Calculate differentials ###
    dat_hcap['Differential'] = (((dat_hcap['Score']-dat_hcap['Rating'])*neutral)/dat_hcap['Slope'])
    ######################################
    ### Pair front and back differentials ###
    ######################################
    ### Slice data into full rounds and nine hole rounds ###
    #cal_fulls = dat_hcap.loc[dat_hcap['Direction'] == dat_direction.iloc[0,0]]
    #cal_fronts = dat_hcap.loc[dat_hcap['Direction'] == dat_direction.iloc[1,0]]
    #cal_backs = dat_hcap.loc[dat_hcap['Direction'] == dat_direction.iloc[2,0]]
    cal_nines = dat_hcap.loc[(dat_hcap.Direction == dat_direction.iloc[1,0]) | (dat_hcap.Direction == dat_direction.iloc[2,0])]
    cal_nines = cal_nines.loc[(cal_nines.Inclusion == 1) | (cal_nines.Inclusion == 2)]
    cal_nines = cal_nines.sort_values('Date', ascending=False)
    ### Check for corresponding back differentials for fronts played ### !!! Not functional!!!
    # This is not neccessary as handicap is based off of paried 9 hole rounds and differntials already account for difference in score
    #if len(cal_fronts) > 0 and len(cal_backs) > 0:
    #    for date in range(len(cal_fronts['Date'])):
    #        course_fr = cal_fronts.iloc[date,1]
    #        date_fr = cal_fronts.iloc[date,0]
    #        diff_fr = cal_fronts.iloc[date,8]
    #        try:
    #            cal_backs_tmp = cal_backs.loc[cal_backs['Course'] == course_fr and cal_backs['Date'] >= date_fr]
    #            if len(cal_backs_tmp) >= 1:
    #                cal_backs_tmp = cal_backs_tmp.iloc[0,:]
    #                bk_index = cal_backs_tmp.index[0]
    #                bk_course = cal_backs_tmp.iloc[0,1]
    #                bk_date = cal_backs_tmp.iloc[0,0]
    #                bk_diff = cal_backs_tmp.iloc[0,8]
    #                
    #                course = course_fr
    #                date_last = bk_date
    #                diff = diff_fr+bk_diff
    #                cal_backs.drop(bk_index)
    #                #!!! COntinue from here !!!
    #                # Add in writting to cal_full table and continue for unmathed front and back pairs
    #        except:
    #            continue
    
    ### Pair 9 hole rounds and update table with paired score differentials ###
    # This will:
    #   update the latest 9 hole round in the pairing with the combined differential
    #   indicate which indecies have been paired
    #   set the score to be included in further calculations for rolling hcap index
    # Calculate net differentials and identify paried indecies
    net_diff = []
    paired_indecies = []
    nines_count = len(cal_nines)
    i = 0
    if nines_count%2 == 0 and nines_count > 1:
        while i in range(nines_count):
            diff_tmp = cal_nines.iloc[i,8]
            diff_tmp2 = cal_nines.iloc[i+1,8]
            net_diff.append(diff_tmp+diff_tmp2)
            paired_indecies.append((cal_nines.index[i], cal_nines.index[i+1]))
            i += 2
            #if i > nines_count 
    elif nines_count%2 > 0 and nines_count >= 3:
        #maxdate = max(cal_nines['Date'])
        #maxdateidx = cal_nines.index[cal_nines['Date'] == maxdate]
        maxdateidx = cal_nines.index.max()
        dat_hcap.loc[dat_hcap.index == maxdateidx, 'Inclusion'] = 2
        cal_nines = cal_nines.drop(maxdateidx)
        nines_count = len(cal_nines)
        while i in range(nines_count):
            diff_tmp = cal_nines.iloc[i,8]
            diff_tmp2 = cal_nines.iloc[i+1,8]
            net_diff.append(diff_tmp+diff_tmp2)
            paired_indecies.append((cal_nines.index[i], cal_nines.index[i+1]))
            i += 2
    elif nines_count == 1:
        singleidx = cal_nines.index[0]
        dat_hcap.loc[dat_hcap.index == singleidx, 'Inclusion'] = 2
        cal_nines = cal_nines.drop(singleidx)
    
    
    # Update table with new net pairings and set inclusion
    if len(paired_indecies) > 0:
        for i in range(len(paired_indecies)):    
            dat_hcap.loc[dat_hcap.index == paired_indecies[i][0], 'Differential'] = net_diff[i] #Inclusion
            dat_hcap.loc[dat_hcap.index == paired_indecies[i][0], 'PairingIdx'] = paired_indecies[i][1]
            dat_hcap.loc[dat_hcap.index == paired_indecies[i][0], 'Inclusion'] = 1
            dat_hcap.loc[dat_hcap.index == paired_indecies[i][1], 'PairingIdx'] = paired_indecies[i][0]
            dat_hcap.loc[dat_hcap.index == paired_indecies[i][1], 'Inclusion'] = 2
    
    # Set inclusion for all full 18 hole rounds
    #dat_hcap.loc[dat_hcap.Direction == dat_direction.iloc[0,0], 'Inclusion'] = 1
    #dat_hcap['Differential'] = dat_hcap['Differential']#.round(decimals=1)
    
    
    ######################################
    ### Calculate Handicap Index for included scores ###
    ######################################
    cal_hidx = dat_hcap.loc[dat_hcap['Inclusion'] == 1]
    hidx_index = cal_hidx.index.values
    #hidx_roll = []
    hidx_incs = []
    #hidx_tmp = cal_hidx.loc[cal_hidx.index <= 7, 'Differential']
    #hidx_vals = hidx_tmp.nsmallest(3)
    #hidx_idx = hidx_vals.index.values
    #hidx = hidx_vals.to_numpy().mean() - 1
    
    ### Loop over table in ascending order to calculate handicap index ###
    for i, index in enumerate(hidx_index):
        #print(str(index), str(i))
        j=i+1
        if j < 20:
            hidx_tmp = cal_hidx.loc[cal_hidx.index <= index, 'Differential']
            if j <= 3:
                hidx_vals = hidx_tmp.nsmallest(1)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean() - 2
            if j == 4:
                hidx_vals = hidx_tmp.nsmallest(1)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean() - 1
            if j == 5:
                hidx_vals = hidx_tmp.nsmallest(1)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
            if j == 6:
                hidx_vals = hidx_tmp.nsmallest(2)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean() - 1
            if j in range(7,9):
                hidx_vals = hidx_tmp.nsmallest(2)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
            if j in range(9,12):
                hidx_vals = hidx_tmp.nsmallest(3)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
            if j in range(12,15):
                hidx_vals = hidx_tmp.nsmallest(4)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
            if j in range(15,17):
                hidx_vals = hidx_tmp.nsmallest(5)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
            if j in range(17,19):
                hidx_vals = hidx_tmp.nsmallest(6)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
            if j == 19:
                hidx_vals = hidx_tmp.nsmallest(7)
                hidx_idx = hidx_vals.index.values
                hidx = hidx_vals.to_numpy().mean()
        if j >= 20:
            hidx_tmp = cal_hidx.loc[cal_hidx.index <= index]
            hidx_tmp = hidx_tmp.nlargest(20, 'Date')
            hidx_tmp = hidx_tmp.loc[:, 'Differntial']
            hidx_vals = hidx_tmp.nsmallest(8)
            hidx_idx = hidx_vals.index.values
            hidx = hidx_vals.to_numpy().mean()
        # Set values in main table.    
        dat_hcap.loc[dat_hcap.index == index, 'Handicap Index'] = hidx
        hidx_incs.append(tuple(hidx_idx))
    
    
    # Set handicap index for non included scores within the calculation of the handicap index.
    # This is to generate viable scores for playing half rounds and calculation the course index
    if calc_noninclusive == 'Y':    
        nones_index = dat_hcap.loc[(dat_hcap['Inclusion'] == 0) | (dat_hcap['Inclusion'] == 2)].index.values
        for index in nones_index:
            if index > 0:
                hidx_copy = dat_hcap.loc[dat_hcap.index == index-1, 'Handicap Index'].to_numpy()
                dat_hcap.loc[dat_hcap.index == index, 'Handicap Index'] = hidx_copy
            elif index == 0:
                dat_hcap.loc[dat_hcap.index == index, 'Handicap Index'] = 0
    
    ### Set the course index ###
    dat_hcap['CourseIdx'] = (dat_hcap['Slope']/neutral)*dat_hcap['Handicap Index']
    
    dat_hcap = dat_hcap.round(decimals=1)
    return dat_hcap

