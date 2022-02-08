################################################################################
# plot_uncompeted_marker_savings_data_prep.py
#
# Build pandas DataFrames which will be used for plotting results of a Scout
# run.
#
# Build the following data sets and output to parquet files
#
# Uncompeted Market Savings
# ./results/plots/uncompeted_market_savings.parquet
#
################################################################################

import os
import json
import pandas as pd

# verify the output directory exists, create it if not.
if not os.path.isdir("./results/plots"):
    os.mkdir("./results/plots")

# ecm_prep (uncompeted market savings)
f = open("./supporting_data/ecm_prep.json")
ecm_prep = json.load(f)
f.close()

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
ums["competed"] = "Uncompeted"

print("Writing ./results/plots/uncompeted_market_savings.parquet")
ums.to_parquet("./results/plots/uncompeted_market_savings.parquet")

################################################################################
###                               End of File                                ###
################################################################################
