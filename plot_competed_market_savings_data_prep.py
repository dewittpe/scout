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

cms = pd.DataFrame()
for ecm in ecm_results_keys:
    print("(" + str(ecm_count) + "/" + str(len(ecm_results_keys)) +\
            ") Extracting Competed Markets Savings for: " + ecm)
    ecm_count = ecm_count + 1
    df1 = pd.DataFrame()
    for ap in list(ecm_results[ecm][CMS].keys()):
        df2 = pd.DataFrame()
        for v in list(ecm_results[ecm][CMS][ap].keys()):
            df3 = pd.DataFrame()
            for rg in list(ecm_results[ecm][CMS][ap][v].keys()):
                df4 = pd.DataFrame()
                for bg in list(ecm_results[ecm][CMS][ap][v][rg].keys()):
                    df5 = pd.DataFrame()
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
                        df5 = pd.concat([df5, x])
                    df4 = pd.concat([df4, df5])
                df3 = pd.concat([df3, df4])
            df2 = pd.concat([df2, df3])
        df1 = pd.concat([df1, df2])
    cms = pd.concat([cms, df1])

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

print("Writing ./results/plots/competed_market_savings.parquet")
cms.to_parquet("./results/plots/competed_market_savings.parquet")

################################################################################
###                               End of File                                ###
################################################################################