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

ums = [{
    'ecm' : ecm,
    'adoption_scenario' : ap,
    'ecc' : ecc,
    'results_scenario' : rs,
    'region' : rg,
    'building_class' : bc,
    'end_use' : eu,
    'year' : yr,
    'value' : value
    }\
            for i   in range(len(ecm_prep)) \
            for ecm in [ecm_prep[i]["name"]] \
            for ap  in list(ecm_prep[i]["markets"].keys())\
            for ecc in list(ecm_prep[i]["markets"][ap]["mseg_out_break"].keys())\
            for rs  in list(ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc].keys())\
            for rg  in list(ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc][rs].keys())\
            for bc  in list(ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc][rs][rg].keys())\
            for eu  in list(ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc][rs][rg][bc].keys())\
            for yr  in list(ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc][rs][rg][bc][eu].keys())\
            for value in   [ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc][rs][rg][bc][eu][yr]]
            ]


print("build one uncompeted_market_savings DataFrame...")
ums = pd.DataFrame.from_dict(ums)

ums["competed"] = "Uncompeted"

ums["construction"] = ""
ums.loc[ums["building_class"].str.contains("New"), "construction"] = "New"
ums.loc[ums["building_class"].str.contains("Existing"), "construction"] = "Existing"

ums.loc[ums["building_class"].str.contains("Residential"), "building_class"] = "Residential"
ums.loc[ums["building_class"].str.contains("Commercial"), "building_class"] = "Commercial"

ums["end_use2"] = ums["end_use"]
ums.loc[ums["end_use"].isin(["Cooling (Equip.)", "Heating (Equip.)", "Ventilation"]), "end_use2"] = "HVAC"
ums.loc[ums["end_use"].isin(["Cooling (Env.)", "Heating (Env.)"]), "end_use2"] = "Envelope"
ums.loc[ums["end_use"].isin(["Computers and Electronics"]), "end_use2"] = "Electronics"

print("Writing ./results/plots/uncompeted_market_savings.parquet")
ums.to_parquet("./results/plots/uncompeted_market_savings.parquet")

################################################################################
###                               End of File                                ###
################################################################################
