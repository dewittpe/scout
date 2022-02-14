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
fm = [{'ecm' : ecm,
      'variable' : v,
      'year' : yr,
      'value' : value
    }\
            for ecm in ecm_results_keys\
            for v in fm_variable_keys\
            for yr in list(ecm_results[ecm]["Financial Metrics"][v].keys())\
            for value in [ecm_results[ecm]["Financial Metrics"][v][yr]]
            ]



print("Build one financial_metrics DataFrame...")
fm = pd.DataFrame.from_dict(fm)

print("Writing ./results/plots/financial_metrics.parquet")
fm.to_parquet("./results/plots/financial_metrics.parquet")

################################################################################
###                               End of File                                ###
################################################################################
