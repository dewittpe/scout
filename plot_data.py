################################################################################
# plot_data.py
#
# Build pandas DataFrames which will be used for plotting results of a Scout
# run.
#
# Build the following data sets:
#
# 1. fm -- Financial Metrics
#
################################################################################

import json
import pandas as pd

# import ecm results data set
f = open("./results/ecm_results.json")
ecm_results = json.load(f)
f.close()

# Get the keys for each level
ecm_keys  = list(ecm_results)
ecm_keys.remove('On-site Generation')

lvl2_keys = list(ecm_results[ecm_keys[0]].keys()) 

# There are several different possible trees from here
# >>> lvl2_keys
# ['Filter Variables', 'Markets and Savings (Overall)',
#  'Markets and Savings (by Category)', 'Financial Metrics']


################################################################################
###                            Financial Metrics                             ###

# explore the data structure a bit
fm_variable_keys = list(ecm_results[ecm_keys[0]]["Financial Metrics"].keys())
fm_variable_keys

# yearly data is at this following levels
for k in fm_variable_keys:
    list(ecm_results[ecm_keys[0]]["Financial Metrics"][k].keys())

# create the fm DataFrame
fm = pd.Dataframe() 
for ecm in ecm_keys:
    for v in fm_variable_keys:
        x = pd.DataFrame.from_dict(
                ecm_results[ecm]["Financial Metrics"][v]
                , orient = 'index'
                , columns = ["value"]
                )
        x['variable'] = v
        x['ecm'] = ecm
        fm = pd.concat([fm, x])

# reset the index and rename -- the index is the year.
fm.reset_index(inplace = True)
fm.rename(columns = {"index" : "year"}, inplace = True)
fm


################################################################################
###                            Financial Metrics                             ###


lvl3_keys = list(ecm_results[ecm_keys[0]][lvl2_keys[

ecm_results[ecms[0]]["Markets and Savings (by Category)"].keys()
ecm_results[ecms[0]]["Markets and Savings (by Category)"]['Max adoption potential'].keys()
ecm_results[ecms[0]]["Markets and Savings (by Category)"]['Max adoption potential']["Baseline Energy Use (MMBtu)"].keys()
ecm_results[ecms[0]]["Markets and Savings (by Category)"]['Max adoption potential']["Baseline Energy Use (MMBtu)"]["AIA CZ1"].keys()
ecm_results[ecms[0]]["Markets and Savings (by Category)"]['Max adoption potential']["Baseline Energy Use (MMBtu)"]["AIA CZ1"]["Commercial (New)"].keys()
ecm_results[ecms[0]]["Markets and Savings (by Category)"]['Max adoption potential']["Baseline Energy Use (MMBtu)"]["AIA CZ1"]["Commercial (New)"]["Heating (Equip.)"].keys()

ecm_results[ecms[0]]["Markets and Savings (by Category)"]['Max adoption potential']["Baseline Energy Use (MMBtu)"]["AIA CZ1"]["Commercial (New)"]["Heating (Equip.)"]



################################################################################
###                               End of File                                ###
################################################################################
