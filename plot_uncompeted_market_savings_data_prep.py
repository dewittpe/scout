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
import re

# verify the output directory exists, create it if not.
if not os.path.isdir("./results/plots"):
    os.mkdir("./results/plots")

# ecm_prep (uncompeted market savings)
f = open("./supporting_data/ecm_prep.json")
ecm_prep = json.load(f)
f.close()

################################################################################
###                               Data Explore                               ###
ecm_prep[0]['fuel_type']
ecm_prep[1]['fuel_type']
ecm_prep[0].keys()

list(ecm_prep[0]["markets"]["Technical potential"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["master_mseg"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"]["baseline"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"]["baseline"]["AIA CZ1"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"]["baseline"]["AIA CZ1"]["Commercial (New)"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"]["baseline"]["AIA CZ1"]["Commercial (New)"]["Heating (Equip.)"].keys())
list(ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"]["baseline"]["AIA CZ1"]["Commercial (New)"]["Heating (Equip.)"]["Electric"].keys())
ecm_prep[0]["markets"]["Technical potential"]["mseg_out_break"]["energy"]["baseline"]["AIA CZ1"]["Commercial (New)"]["Heating (Equip.)"]["Electric"]["2045"]


################################################################################
###                                Fuel Types                                ###
uft = [{
    'ecm' : ecm,
    'fuel_type_level' : ftlvl,
    'fuel_type' : ft
    }\
            for i      in range(len(ecm_prep))
            for ecm    in [ecm_prep[i]["name"]]
            for ftlvl  in list(ecm_prep[i]["fuel_type"].keys())
            for ft     in [ecm_prep[i]["fuel_type"][ftlvl]]
            ]
uft = pd.DataFrame.from_dict(uft)
uft

################################################################################
###                        Uncompeted Market Savings                         ###
print("build one uncompeted_market_savings DataFrame...")

# After getting to the level with end use there can be a fuel_type or the year,
# or nothing.  So start building a dictionary to get to that level and then
# process futher.

ums = [{
    'ecm' : ecm,
    'adoption_scenario' : ap,
    'ecc' : ecc,
    'results_scenario' : rs,
    'region' : rg,
    'building_class' : bc,
    'end_use' : eu,
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
            for value in   [ecm_prep[i]["markets"][ap]["mseg_out_break"][ecc][rs][rg][bc][eu]]
            ]

# omit any element of the ums list that has a zero length value
ums = [ums[i] for i in range(len(ums)) if len(ums[i]["value"]) > 0]

# get the keys beyond end use
has_fuel_type  = [ums[i] for i in range(len(ums)) if list(ums[i]["value"].keys()) == ['Electric', 'Non-Electric']]
sans_fuel_type = [ums[i] for i in range(len(ums)) if not list(ums[i]["value"].keys()) == ['Electric', 'Non-Electric']]

ums_sans_fuel_type = [
        {
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
                    for i   in range(len(sans_fuel_type)) 
                    for ecm in [sans_fuel_type[i]["ecm"]] 
                    for ap  in [sans_fuel_type[i]["adoption_scenario"]]
                    for ecc in [sans_fuel_type[i]["ecc"]]
                    for rs in [sans_fuel_type[i]["results_scenario"]]
                    for rg in [sans_fuel_type[i]["region"]]
                    for bc in [sans_fuel_type[i]["building_class"]]
                    for eu in [sans_fuel_type[i]["end_use"]]
                    for yr  in list(sans_fuel_type[i]["value"].keys()) 
                    for value in   [sans_fuel_type[i]["value"][yr]]
                    ]
pd.DataFrame.from_dict(ums_sans_fuel_type)

sans_fuel_type[0]["value"]

def isyear(l):
    regex = re.compile(r"\d{4}")
    out = [regex.search(k) for k in l]
    return any(out)

has_fuel_type = [not isyear(list(ums[i]["value"].keys())) for i in range(len(ums))]

def foo(i):
    if has_fuel_type[i]:
        hft = [{
            "fuel_type" : ft,
            "year" : yr,
            "value" : value
            }\
                    for ft in list(ums[i]["value"].keys())
                    for yr in list(ums[i]["value"][ft].keys())
                    for value in [ums[i]["value"][ft][yr]]
                    ]
    else:
        hft = [{
            "fuel_type" : "",
            "year" : yr,
            "value" : value
            }\
                    for yr in list(ums[i]["value"].keys())
                    for value in [ums[i]["value"][yr]]
                    ]
    ums2 = [{
            'ecm' : ums[i]["ecm"],
            'adoption_scenario' : ums[i]["adoption_scenario"],
            'ecc' : ums[i]["ecc"],
            'results_scenario' : ums[i]["results_scenario"],
            'region' : ums[i]["region"],
            'building_class' : ums[i]["building_class"],
            'end_use' : ums[i]["end_use"],
            'fuel_type' : hft[j]["fuel_type"],
            'year' : hft[j]["year"],
            'value' : hft[j]["value"]
            }\
                    for j in range(len(hft))]
    return ums2

pd.DataFrame.from_dict(foo(22))
pd.DataFrame.from_dict(foo(21))



len(ums[21]["value"]) 
has_fuel_type[21]
foo(21)
isyear(list(ums[21]["value"].keys()))

ums = [foo(i) for i in range(len(ums))]
ums = pd.DataFrame.from_dict(ums)
ums

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


################################################################################
###                                  Checks                                  ###
ums

ums["fuel_type"].value_counts(dropna = False)
ums[ums["fuel_type"].notna()]

ums[ums["ecm"] == "Prospective Commercial CCHP"]
ums[(ums["ecm"] == "Prospective Commercial CCHP") & (ums["end_use"] == "Heating (Equip.)")]
ums[(ums["ecm"] == "Prospective Commercial CCHP") & (ums["end_use"] == "Heating (Equip.)") & (ums.value.notna())]

pd.set_option('display.max.rows', None)
print(ums[(ums["ecm"] == "Prospective Commercial CCHP") & (ums["end_use"] == "Heating (Equip.)") & (ums.value.notna())])



print("Writing ./results/plots/uncompeted_market_savings.parquet")
ums.to_parquet("./results/plots/uncompeted_market_savings.parquet")

################################################################################
###                               End of File                                ###
################################################################################
