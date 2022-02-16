################################################################################
# plot_competed_market_savings_data_prep.py
#
# Build pandas DataFrames which will be used for plotting results of a Scout
# run.
#
# Build the following data sets and output to parquet files
#
# Competed Market Savings
# ./results/plots/competed_market_savings.parquet
#
################################################################################

import os
import json
import pandas as pd
import re

# verify the output directory exists, create it if not.
if not os.path.isdir("./results/plots"):
    os.mkdir("./results/plots")

# import ecm results data set (competed and financial metrics)
f = open("./results/ecm_results.json")
ecm_results = json.load(f)
f.close()

# Get the keys for each level
ecm_results_keys  = list(ecm_results)
ecm_results_keys.remove('On-site Generation')

lvl2_keys = list(ecm_results[ecm_results_keys[0]].keys())

# There are several different possible trees from here
# >>> lvl2_keys
# ['Filter Variables', 'Markets and Savings (Overall)',
#  'Markets and Savings (by Category)', 'Financial Metrics']

################################################################################
##                         Competed Market Savings                          ###
print("Build one competed_market_savings DataFrame...")
CMS = "Markets and Savings (by Category)"

cms = [{
    'ecm' : ecm,
    'adoption_scenario' : ap,
    'variable' : v,
    'region' : rg,
    'building_class' : bg,
    'end_use' : eu,
    'value' : value
    }\
        for ecm in ecm_results_keys
        for ap  in list(ecm_results[ecm][CMS].keys())
        for v   in list(ecm_results[ecm][CMS][ap].keys())
        for rg  in list(ecm_results[ecm][CMS][ap][v].keys())
        for bg  in list(ecm_results[ecm][CMS][ap][v][rg].keys())
        for eu  in list(ecm_results[ecm][CMS][ap][v][rg][bg].keys())
        for value in   [ecm_results[ecm][CMS][ap][v][rg][bg][eu]]
        ]

# the value element forks depending on the presence/absence of split fuel.  So,
# split the dictionary and build two lists
#
# TODO: Modify the code in run.py so that fuel_type is a element of all output.
# then the list construciton above could be used for all cases and this forking
# logic would no longer be needed.

regex = re.compile(r"\d{4}")

has_fuel_type = [regex.search(list(cms[i]["value"].keys())[0]) is None for i in range(len(cms))]

# THE FOLLOWING IS FLAWED THE FOR LOOP ISN"T GOING TO GIVE YOU WANT YOU WANT
exit(1)
def foo(i):
    if has_fuel_type[i]:
        hft = [{
            "fuel_type" : ft,
            "year" : yr,
            "value" : value
            }\
                    for ft in list(cms[i]["value"].keys())
                    for yr in list(cms[i]["value"][ft].keys())
                    for value in [cms[i]["value"][ft][yr]]
                    ]
    else:
        hft = [{
            "fuel_type" : "",
            "year" : yr,
            "value" : value
            }\
                    for yr in list(cms[i]["value"].keys())
                    for value in [cms[i]["value"][yr]]
                    ]
    for j in range(len(hft)) :
        cms2 = {
                'ecm' : cms[i]["ecm"],
                'adoption_scenario' : cms[i]["adoption_scenario"],
                'variable' : cms[i]["variable"],
                'region' : cms[i]["region"],
                'building_class' : cms[i]["building_class"],
                'end_use' : cms[i]["end_use"],
                'fuel_type' : hft[j]["fuel_type"],
                'year' : hft[j]["year"],
                'value' : hft[j]["value"]
                }
    return cms2

cms = [foo(i) for i in range(len(cms))]
cms = pd.DataFrame.from_dict(cms)
cms

# add some more columns
cms["competed"] = "Competed"
cms["results_scenario"] = "savings"

cms.loc[cms["variable"].str.contains("Baseline"), "results_scenario"] = "baseline"
cms.loc[cms["variable"].str.contains("Efficient"), "results_scenario"] = "efficient"

cms["ecc"] = "carbon"
cms.loc[cms["variable"].str.contains("Energy"), "ecc"] = "energy"
cms.loc[cms["variable"].str.contains("Cost"), "ecc"] = "cost"

cms["construction"] = ""
cms.loc[cms["building_class"].str.contains("New"), "construction"] = "New"
cms.loc[cms["building_class"].str.contains("Existing"), "construction"] = "Existing"

cms.loc[cms["building_class"].str.contains("Residential"), "building_class"] = "Residential"
cms.loc[cms["building_class"].str.contains("Commercial"), "building_class"] = "Commercial"

cms["end_use2"] = cms["end_use"]
cms.loc[cms["end_use"].isin(["Cooling (Equip.)", "Heating (Equip.)", "Ventilation"]), "end_use2"] = "HVAC"
cms.loc[cms["end_use"].isin(["Cooling (Env.)", "Heating (Env.)"]), "end_use2"] = "Envelope"
cms.loc[cms["end_use"].isin(["Computers and Electronics"]), "end_use2"] = "Electronics"

# check
# cms[["end_use", "end_use2"]].value_counts()

print("Writing ./results/plots/competed_market_savings.parquet")
cms.to_parquet("./results/plots/competed_market_savings.parquet")

################################################################################
###                               End of File                                ###
################################################################################
