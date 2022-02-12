################################################################################
# plot_financial_metrics_data_prep.py
#
# Build pandas DataFrames which will be used for plotting results of a Scout
# run.
#
#  Financial Metrics
#  ./results/plots/financial_metrics.parquet
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
fm = []
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
        fm.append(x)

print("Concat to one DataFrame...")
fm = pd.concat(fm)

# reset the index and rename -- the index is the year.
fm.reset_index(inplace = True)
fm.rename(columns = {"index" : "year"}, inplace = True)

print("Writing ./results/plots/financial_metrics.parquet")
fm.to_parquet("./results/plots/financial_metrics.parquet")

################################################################################
###                               End of File                                ###
################################################################################
