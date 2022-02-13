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
CMS = "Markets and Savings (by Category)"

ecm_count = 1

cms = []
for ecm in ecm_results_keys:
    print("(" + str(ecm_count) + "/" + str(len(ecm_results_keys)) +\
            ") Extracting Competed Markets Savings for: " + ecm)
    ecm_count = ecm_count + 1
    for ap in list(ecm_results[ecm][CMS].keys()):
        for v in list(ecm_results[ecm][CMS][ap].keys()):
            for rg in list(ecm_results[ecm][CMS][ap][v].keys()):
                for bg in list(ecm_results[ecm][CMS][ap][v][rg].keys()):
                    for eu in list(ecm_results[ecm][CMS][ap][v][rg][bg].keys()):
                        x = pd.DataFrame.from_dict(
                                ecm_results[ecm][CMS][ap][v][rg][bg][eu]
                                , orient = 'index'
                                , columns = ['value']
                                )
                        x['end_use'] = eu
                        x['building_class'] = bg
                        x['region'] = rg
                        x['variable'] = v
                        x['adoption_scenario'] = ap
                        x['ecm'] = ecm
                        cms.append(x)

print("Concat to one DataFrame...")
cms = pd.concat(cms)

# reset the index and rename -- the index is the year.
cms.reset_index(inplace = True)
cms.rename(columns = {"index" : "year"}, inplace = True)

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
