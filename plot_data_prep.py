################################################################################
# plot_data_prep.py
#
# Build pandas DataFrames which will be used for plotting results of a Scout
# run.
#
# Build the following data sets and output to parquet files
#
# 1. fm
#       -- Financial Metrics
#       -- ./results/plots/financial_metrics.parquet
# 2. cms
#       -- Competed Market Savings
#       -- ./results/plots/competed_market_savings.parquet
# 3. ums
#       -- Uncompeted Market Savings
#       -- ./results/plots/uncompeted_market_savings.parquet
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

# ecm_prep (uncompeted market savings)
f = open("./supporting_data/ecm_prep.json")
ecm_prep = json.load(f)
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
###                            Financial Metrics                             ###

# explore the data structure a bit
fm_variable_keys = \
        list(ecm_results[ecm_results_keys[0]]["Financial Metrics"].keys())
fm_variable_keys

# yearly data is at this following levels
for k in fm_variable_keys:
    list(ecm_results[ecm_results_keys[0]]["Financial Metrics"][k].keys())

# create the fm DataFrame
ecm_count = 1
fm = pd.DataFrame()
for ecm in ecm_results_keys:
    print("(" + str(ecm_count) + "/" + str(len(ecm_results_keys)) +\
            ") Extracting Financial Metrics for: " + ecm)
    ecm_count = ecm_count + 1
    for v in fm_variable_keys:
        x = pd.DataFrame.from_dict(
                ecm_results[ecm]["Financial Metrics"][v]
                , orient = 'index'
                , columns = ['value']
                )
        x['variable'] = v
        x['ecm'] = ecm
        fm = pd.concat([fm, x])

# reset the index and rename -- the index is the year.
fm.reset_index(inplace = True)
fm.rename(columns = {"index" : "year"}, inplace = True)

print("Writing ./results/plots/financial_metrics.parquet")
fm.to_parquet("./results/plots/financial_metrics.parquet")

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

print("Writing ./results/plots/competed_market_savings.parquet")
cms.to_parquet("./results/plots/competed_market_savings.parquet")

################################################################################
###                        Uncompeted Market Savings                         ###

ums = pd.DataFrame()
for i in range(len(ecm_prep)):
    ecm = ecm_prep[i]["name"]
    print("(" + str(i + 1) + "/" + str(len(ecm_prep)) +\
            ") Extracting Uncompeted Markets Savings for: " + ecm)
    df1 = pd.DataFrame()
    for ap in list(ecm_prep[i]["markets"].keys()):
        df2 = pd.DataFrame()
        for ecc in list(ecm_prep[i]["markets"][ap]["mseg_out_break"].keys()):
            df3 = pd.DataFrame()
            for rs in list(ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc]\
                    .keys()):
                df4 = pd.DataFrame()
                for rg in list(ecm_prep[i]["markets"][ap]["mseg_out_break"]\
                        [ecc][rs].keys()):
                    df5 = pd.DataFrame()
                    for bc in list(ecm_prep[i]["markets"][ap]["mseg_out_break"]\
                            [ecc][rs][rg].keys()):
                        df6 = pd.DataFrame()
                        for eu in list(ecm_prep[i]["markets"][ap]\
                                ["mseg_out_break"][ecc][rs][rg][bc].keys()):
                            d = ecm_prep[i]["markets"][ap]["mseg_out_break"]\
                                    [ecc][rs][rg][bc][eu]
                            if (len(d) > 0):
                                x = pd.DataFrame.from_dict(
                                        d
                                        , orient = 'index'
                                        , columns = ['value'])
                                x['end_use'] = eu
                                x['building_class'] = bc
                                x['region'] = rg
                                x['results_scenario'] = rs
                                x['ecc'] = ecc
                                x['adoption_scenario'] = ap
                                x['ecm'] = ecm
                                df6 = pd.concat([df6, x])
                        df5 = pd.concat([df5, df6])
                    df4 = pd.concat([df4, df5])
                df3 = pd.concat([df3, df4])
            df2 = pd.concat([df2, df3])
        df1 = pd.concat([df1, df2])
    ums = pd.concat([ums, df1])

# reset the index and rename -- the index is the year.
ums.reset_index(inplace = True)
ums.rename(columns = {"index" : "year"}, inplace = True)

print("Writing ./results/plots/uncompeted_market_savings.parquet")
ums.to_parquet("./results/plots/uncompeted_market_savings.parquet")

################################################################################
###                               End of File                                ###
################################################################################
