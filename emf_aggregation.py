import sys, getopt
import os.path
import numpy as np
import pandas as pd
from plots_utilities import json_to_df
from plots_utilities import ECM_PREP
from plots_utilities import ECM_RESULTS

# dev work
# ecm_results_v1 = ECM_RESULTS("./results/ecm_results_v1.json").mas_by_category
# ecm_results_v2 = ECM_RESULTS("./results/ecm_results_v2.json").mas_by_category
# ecm_results_v3 = ECM_RESULTS("./results/ecm_results_v3.json").mas_by_category
# ecm_results_v4 = ECM_RESULTS("./results/ecm_results_v4.json").mas_by_category
# ecm_results_v5 = ECM_RESULTS("./results/ecm_results_v5.json").mas_by_category
# ecm_results_v6 = ECM_RESULTS("./results/ecm_results_v6.json").mas_by_category

# ecm_results_v1.columns
# ecm_results_v2.columns
# ecm_results_v3.columns
# ecm_results_v4.columns
# ecm_results_v5.columns
# ecm_results_v6.columns

# set(ecm_results_v3.building_type)


# set(ecm_results_v4.split_fuel)
# {'Biomass', 'Propane', 'Electric', 'Natural Gas', None, 'Distillate/Other'}

################################################################################
# mappings between ECM results and EMF aggregtaions
emf_base_string =\
    pd.DataFrame(data = {
        "Avoided CO\u2082 Emissions (MMTons)" : "*Emissions|CO2|Energy|Demand|Buildings",
        "Energy Savings (MMBtu)"              : "*Final Energy|Buildings"
        }.items(),
        columns = ["impact", "emf_base_string"]
        )

# Unit conversions.
# The value column is in MMBtu and needs to be in EJ (extajuls)
MMBtu_to_EJ           = 1.05505585262e-9
EJ_to_quad            = 0.9478
pound_to_mt           = 0.000453592
EJ_to_twh             = 277.778
EJ_to_mt_co2_propane  = EJ_to_quad * 62.88
EJ_to_mt_co2_kerosene = EJ_to_quad * 73.38
EJ_to_mt_co2_gas      = EJ_to_quad * 53.056
EJ_to_mt_co2_oil      = EJ_to_quad * 74.14
EJ_to_mt_co2_bio      = EJ_to_quad * 96.88

# NOTE: Mapping to EMF fuel types _might_ require a mapping that uses both fuel
# type and end use.  In the example script the combination of fuel_type = "distillate" and
# end_use = "secondary heating (kerosene)" maps to "Oil_kerosene".
# 
# Other possible end uses that will need to be accounted for,
#   * stove (wood)
#   * secondary heater (wood)

# For all but scout_split_fuel == "other fuel"
emf_fuel_types =\
        pd.DataFrame(data = {
              ("Natural Gas"      , "Gas"             , EJ_to_mt_co2_gas)
            , ("natural gas"      , "Gas"             , EJ_to_mt_co2_gas)
            , ("Propane"          , "Gas_lpg"         , EJ_to_mt_co2_propane)
            , ("Distillate/Other" , "Oil"             , EJ_to_mt_co2_oil)
            , ("distillate"       , "Oil"             , EJ_to_mt_co2_oil)
            , ("Biomass"          , "Biomass Solids"  , EJ_to_mt_co2_oil)
            , ("Electric"         , "Electricity"     , EJ_to_twh)
            , ("Electricity"      , "Electricity"     , EJ_to_twh)
            , ("electricity"      , "Electricity"     , EJ_to_twh)
            }
            ,
            columns = ["scout_split_fuel", "emf_fuel_type", "emf_CO2_conversion_factor"]
            )

emf_other_fuel_types =\
        pd.DataFrame(data = {
              ("other fuel" , "heating"           , "furnance (LPG)"               , "Oil"            , EJ_to_mt_co2_propane)
            , ("other fuel" , "heating"           , "furnance (kerosene)"          , "Oil"            , EJ_to_mt_co2_kerosene)
            , ("other fuel" , "heating"           , "stove (wood)"                 , "Biomass Solids" , EJ_to_mt_co2_bio)
            , ("other fuel" , "secondary heating" , "secondary heater (wood)"      , "Biomass Solids" , EJ_to_mt_co2_bio)
            , ("other fuel" , "secondary heating" , "secondary heater (coal)"      , "Biomass Solids" , EJ_to_mt_co2_bio)
            , ("other fuel" , "secondary heating" , "secondary heater (kerosene)"  , "Oil"            , EJ_to_mt_co2_kerosene)
            , ("other fuel" , "secondary heating" , "secondary heater (LPG)"       , "Oil"            , EJ_to_mt_co2_propane)
            , ("other fuel" , "water heating"     , np.nan                         , "Oil"            , EJ_to_mt_co2_oil)
            , ("other fuel" , "cooking"           , np.nan                         , "Oil"            , EJ_to_mt_co2_oil)
            , ("other fuel" , "drying"            , np.nan                         , "Oil"            , EJ_to_mt_co2_oil)
            , ("other fuel" , "other"             , np.nan                         , "Oil"            , EJ_to_mt_co2_oil)
            }
            , columns = ["scout_split_fuel", "scout_end_use", "scout_technology_type", "emf_fuel_type", "emf_CO2_conversion_factor"])

emf_direct_indirect_fuel =\
        pd.DataFrame(data = {
              "Natural Gas"      : "Direct"
            , "natural gas"      : "Direct"
            , "Distillate/Other" : "Direct"
            , "distillate"       : "Direct"
            , "Biomass"          : "Direct"
            , "Propane"          : "Direct"
            , "Electric"         : "Indirect"
            , "electricity"      : "Indirect"
            , "Non-Electric"     : "Direct"
            , "other fuel"       : "Direct"
            }.items(),
            columns = ["scout_split_fuel", "emf_direct_indirect_fuel"]
            )

emf_end_uses =\
        pd.DataFrame(data = {
              "Cooking"                   : "Appliances"  # ecm_results
            , "Cooling (Env.)"            : np.nan        # ecm_results
            , "Cooling (Equip.)"          : "Cooling"     # ecm_results
            , "Computers and Electronics" : "Other"       # ecm_results
            , "Heating (Env.)"            : np.nan        # ecm_results
            , "Heating (Equip.)"          : "Heating"     # ecm_results
            , "Lighting"                  : "Lighting"    # ecm_results
            , "Other"                     : "Other"       # ecm_results
            , "Refrigeration"             : "Appliances"  # ecm_results
            , "Ventilation"               : "Heating"     # ecm_results
            , "Water Heating"             : "Appliances"  # ecm_results
            , 'ceiling fan'               : "Appliances"  # baseline
            , "cooking"                   : "Appliances"  # baseline
            , 'cooling'                   : "Cooling"     # baseline
            , 'computers'                 : "Other"       # baseline
            , 'drying'                    : "Appliances"  # baseline
            , 'fans and pumps'            : "Heating"     # baseline
            , 'heating'                   : "Heating"     # baseline
            , 'lighting'                  : "Lighting"    # baseline
            , 'MELs'                      : "Other"       # baseline
            , 'non-PC office equipment'   : "Other"       # baseline
            , 'other'                     : "Other"       # baseline
            , 'onsite generation'         : np.nan        # baseline
            , 'PCs'                       : "Other"       # baseline
            , 'refrigeration'             : "Appliances"  # baseline
            , 'secondary heating'         : "Heating"     # baseline
            , 'TVs'                       : "Other"       # baseline
            , 'ventilation'               : "Heating"     # baseline
            , 'water heating'             : "Appliances"  # baseline
            }.items(),
            columns = ["scout_end_use", "emf_end_use"]
            )

# if building_class exists, then part into to two columns
building_class_construction =\
        pd.DataFrame.from_dict(data = {
            "Commercial (Existing)"  : {
                "building_class" : "Commercial",
                "building_construction" : "Existing"
                },
            "Commercial (New)": {
                "building_class" : "Commercial",
                "building_construction" : "New"
                },
            "Residential (Existing)" : {
                "building_class" : "Residential",
                "building_construction" : "Existing"
                },
            "Residential (New)": {
                "building_class" : "Residential",
                "building_construction" : "New"
                }
            }, orient = "index")\
                    .reset_index()\
                    .rename(columns = {"index" : "building_class0"})

building_type_to_class =\
        pd.DataFrame(data = {
              'Assembly/Other'       : "Commercial"
            , 'Education'            : "Commercial"
            , 'Hospitality'          : "Commercial"
            , 'Hospitals'            : "Commercial"
            , 'Large Offices'        : "Commercial"
            , 'Multi Family Homes'   : "Residential"
            , 'Retail'               : "Commercial"
            , 'Single Family Homes'  : "Residential"
            , 'Small/Medium Offices' : "Commercial"
            , "Warehouse"            : "Commercial" # ecm_results
            , "assembly"           : "Commercial"
            , "education"          : "Commercial"
            , "food sales"         : "Commercial"
            , "food service"       : "Commercial"
            , "health care"        : "Commercial"
            , "lodging"            : "Commercial"
            , "large office"       : "Commercial"
            , "small office"       : "Commercial"
            , "mercantile/service" : "Commercial"
            , "warehouse"          : "Commercial"
            , "other"              : "Commercial"
            , "single family home" : "Residential"
            , "multi family home"  : "Residential"
            , "mobile home"        : "Residential"
            , "Mobile Homes"       : "Residential"
            }.items(),
            columns = ["building_type", "building_class"]
            )

################################################################################

################################################################################
# Define some help documentation which will be conditionally shown to the end
# user.
help_usage = "Usage: emf_aggregation.py [options]"
help_options = """
Options:
  -h --help          Print this help and exit
  --ecm_prep=FILE    Path to a ecm_prep.json FILE, the results of ecm_prep.py
  --ecm_results=FILE Path to a ecm_results.json FILE, the results of run.py
"""

if __name__ == "__main__":
    # get command line args
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:", ["help", "ecm_results=", "ecm_prep="])
    except getopt.GetoptError:
        print(help_usage)
        print("Get more details by running: python emf_aggregation.py -h")
        sys.exit(2)

    # set default values for command line arguments
    ecm_prep_path    = "./supporting_data/ecm_prep.json"
    ecm_results_path = "./results/ecm_results.json"
    baseline_path    = "./supporting_data/stock_energy_tech_data/mseg_res_com_emm"
    emf_output_path  = "./emf_output"

    if not os.path.exists(emf_output_path):
        os.makedirs(emf_output_path)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_usage)
            print(help_options)
            sys.exit()
        elif opt in ("--ecm_results"):
            ecm_results_path = arg
        elif opt in ("--ecm_prep"):
            ecm_prep_path = arg

    if not os.path.exists(ecm_prep_path):
        print(f"{ecm_prep_path} can not be reached or does not exist.")
        sys.exit(1)
    if not os.path.exists(ecm_results_path):
        print(f"{ecm_results_path} can not be reached or does not exist.")
        sys.exit(1)

    ############################################################################
    # Import the Data sets
    # print(f"Importing data from {ecm_prep_path}")
    # ecm_prep = ECM_PREP(path = ecm_prep_path)

    print(f"Importing data from {ecm_results_path}")
    ecm_results = ECM_RESULTS(path = ecm_results_path).mas_by_category

    print(f"Importing data from {baseline_path}")
    baseline = json_to_df(path = baseline_path)

    print(f"Importing coversion coeffs_emm")
    coeffs_emm = json_to_df(path = "./supporting_data/convert_data/emm_region_emissions_prices.json")

    ############################################################################
    # Data clean up for baseline
    print("Cleaning and pre-processing baseline data")
    #
    # Per conversation with Chioke this is the outline of the structure of
    # baseline json file
    #     lvl0: Region
    #     lvl1: building_type
    #     lvl2:
    #       one of two things:
    #       1. building type metadata
    #       2. fuel_type
    #
    #     lvl3:
    #       if lvl2 is building type metadata then lvl3 the year (lvl4 value)
    #       if lvl2 is fuel type lvl3 is _always_ end_use
    #
    #     lvl4:
    #       One of four things:
    #       1. values if lvl2 was building metadata
    #       2. if lvl2 is fuel type then
    #          a. supply/demand key if lvl3 is a heating or cooling end use
    #             (includes secondary heating)
    #          b. technology_type or
    #          c. stock/energy keys
    #
    #     lvl5
    #       if (lvl4 = 2a) then technology_type / envelope components
    #       if (lvl4 = 2b) then stock/energy keys
    #       if (lvl4 = 2c) year or NA
    #
    #     lvl6
    #       if (lvl4 = 2c) value
    #       if (lvl5 is stock/energy key) then NA or year
    #       if (lvl5 is technology_type / envelope components) then stock/energy
    #          key
    #
    #     lvl7
    #       values or years
    #
    #     lvl8
    #       values

    # omit some rows with data on number of buildings
    keep = ~baseline.lvl2.isin(["new homes", "total square footage",
        "new square footage", "total homes"])
    baseline = baseline[keep]
    baseline.reset_index(inplace = True, drop = True)

    # remove useless rows
    baseline = baseline[~((baseline.lvl6 == "stock") & (baseline.lvl7 == "NA")) ]
    baseline = baseline[~((baseline.lvl5 == "stock") & (baseline.lvl6 == "NA")) ]
    baseline = baseline[~((baseline.lvl4 == "stock") & (baseline.lvl5 == "NA")) ]

    # if stock/energy is in lvl4 then
    baseline.loc[baseline.lvl4.isin(["stock", "energy"]),:]
    baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl8"] = baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl6"]
    baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl7"] = baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl5"]
    baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl6"] = baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl4"]
    baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl5"] = np.nan
    baseline.loc[baseline.lvl4.isin(["stock", "energy"]), "lvl4"] = np.nan

    # if stock/energy is in lvl5 then
    baseline.loc[baseline.lvl5.isin(["stock", "energy"]),:]
    baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl8"] =\
        baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl7"]
    baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl7"] =\
        baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl6"]
    baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl6"] =\
        baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl5"]
    baseline.loc[baseline.lvl5.isin(["stock", "energy"]), "lvl5"] = np.nan

    # when lvl4 is supply demand, and the above has been done, then lvl5 is all
    # missing values and data can be shifted
    baseline.loc[baseline.lvl4.isin(["supply", "demand"]),"lvl3"]

    baseline.loc[~baseline.lvl4.isin(["supply", "demand"]),"lvl5"] = \
        baseline.loc[~baseline.lvl4.isin(["supply", "demand"]),"lvl4"]
    baseline.loc[~baseline.lvl4.isin(["supply", "demand"]),"lvl4"] = np.nan

    baseline.rename(
            columns = {
                "lvl0" : "region",
                "lvl1" : "building_type",
                "lvl2" : "fuel_type",
                "lvl3" : "end_use",
                "lvl4" : "supply_demand",
                "lvl5" : "technology_type",
                "lvl6" : "stock_energy",
                "lvl7" : "year",
                "lvl8" : "value"
                },
            inplace = True)

    baseline["emf_base_string"] = "*Final Energy|Buildings"

    baseline = baseline\
            .merge(
                    building_type_to_class,
                    how = "left",
                    on = "building_type"
                    )\
            .merge(
                    emf_end_uses,
                    how = "left",
                    left_on = "end_use",
                    right_on = "scout_end_use")

    baseline.value = baseline.value.apply(float)
    baseline.year  = baseline.year.apply(int)

    ############################################################################
    # Data clean up for ecm_results
    # reduce rows to only the needed impacts:
    print("Cleaning and pre-processing ecm_results data")
    ecm_results =\
            ecm_results.merge(emf_base_string, how = "inner", on = "impact")

    # merge on emf_fuel types and end uses
    if "split_fuel" in ecm_results.columns:
        ecm_results = \
                ecm_results\
                .merge(
                        emf_fuel_types,
                        how = "left",
                        left_on = "split_fuel",
                        right_on = "scout_split_fuel"
                        )\
            .merge(
                    emf_direct_indirect_fuel,
                    how = "left",
                    left_on = "split_fuel",
                    right_on = "scout_split_fuel"
                    )
    else:
        print("Error: split_fuel is not a column in the ecm_results.")
        sys.exit(1)

    # if building_class is part of the ecm_results then split into two columns
    if "building_class" in ecm_results.columns:
        ecm_results = \
            ecm_results\
            .merge(
                    right = building_class_construction,
                    how = "left",
                    left_on = "building_class",
                    right_on = "building_class0",
                    suffixes = ("_x", "")
                    )\
            .drop(columns = ["building_class0", "building_class_x"])

    if "building_type" in ecm_results.columns:
        ecm_results = \
            ecm_results\
            .merge(
                    right = building_type_to_class,
                    how = "left",
                    on = "building_type"
                    )


    if "end_use" in ecm_results.columns:
        ecm_results = \
                ecm_results\
            .merge(
                    emf_end_uses,
                    how = "left",
                    left_on = "end_use",
                    right_on = "scout_end_use"
                    )\
            .drop(columns = ["end_use"])


    # Convert MMBtu to Exajoules
    idx = ecm_results.impact.str.contains("MMBtu")
    ecm_results.loc[idx, "value"] *= 1.05505585262e-9
    ecm_results.impact = ecm_results.impact.str.replace("MMBtu", "EJ")

    ############################################################################
    # Data clean up coeffs_emm
    print("Cleaning up coeffs_emm")
    coeffs_emm = \
        coeffs_emm[(coeffs_emm.lvl0 == "CO2 intensity of electricity") &
                   (coeffs_emm.lvl1 == "data")
                   ]

    coeffs_emm = \
        coeffs_emm\
        .drop(columns = ["lvl0", "lvl1", "lvl5"])\
        .rename(columns = {
            "lvl2" : "region",
            "lvl3" : "year",
            "lvl4" : "CO2_intensity_of_electricity"
            })

    coeffs_emm.CO2_intensity_of_electricity =\
            coeffs_emm.CO2_intensity_of_electricity.apply(float)
    coeffs_emm.year = coeffs_emm.year.apply(int)

    ############################################################################
    # ECM Results aggregations:
    print("aggregating ecm_results to EMF summary")
    a0 = ecm_results\
            .groupby(["region", "emf_base_string", "year"])\
            .agg(value = ("value", "sum"))

    a1 = ecm_results\
            .groupby(["region", "emf_base_string", "building_class", "year"])\
            .agg(value = ("value", "sum"))

    a2 = ecm_results\
            .groupby(["region", "emf_base_string", "building_class", "emf_end_use", "year"])\
            .agg(value = ("value", "sum"))

    a3_0 = ecm_results\
            [ecm_results.emf_base_string == "*Emissions|CO2|Energy|Demand|Buildings"]\
            .groupby(["region", "emf_base_string", "emf_direct_indirect_fuel", "year"])\
            .agg(value = ("value", "sum"))
    a3_1 = ecm_results\
            [ecm_results.emf_base_string == "*Emissions|CO2|Energy|Demand|Buildings"]\
            .groupby(["region", "emf_base_string", "building_class", "emf_direct_indirect_fuel", "year"])\
            .agg(value = ("value", "sum"))
    a3_2 = ecm_results\
            [ecm_results.emf_base_string == "*Emissions|CO2|Energy|Demand|Buildings"]\
            .groupby(["region", "emf_base_string", "building_class", "emf_end_use", "emf_direct_indirect_fuel", "year"])\
            .agg(value = ("value", "sum"))

    a4_0 = ecm_results\
            [ecm_results.emf_base_string == "*Final Energy|Buildings"]\
            .groupby(["region", "emf_base_string", "emf_fuel_type", "year"])\
            .agg(value = ("value", "sum"))
    a4_1 = ecm_results\
            [ecm_results.emf_base_string == "*Final Energy|Buildings"]\
            .groupby(["region", "emf_base_string", "building_class", "emf_fuel_type", "year"])\
            .agg(value = ("value", "sum"))
    a4_2 = ecm_results\
            [ecm_results.emf_base_string == "*Final Energy|Buildings"]\
            .groupby(["region", "emf_base_string", "building_class", "emf_end_use", "emf_fuel_type", "year"])\
            .agg(value = ("value", "sum"))

    # Aggregation clean up
    a0.reset_index(inplace = True)
    a1.reset_index(inplace = True)
    a2.reset_index(inplace = True)
    a3_0.reset_index(inplace = True)
    a3_1.reset_index(inplace = True)
    a3_2.reset_index(inplace = True)
    a4_0.reset_index(inplace = True)
    a4_1.reset_index(inplace = True)
    a4_2.reset_index(inplace = True)

    # build the full emf_string
    a0["emf_string"] = a0.region + a0.emf_base_string
    a1["emf_string"] = a0.region + a1.emf_base_string + "|" + a1.building_class
    a2["emf_string"] = a0.region + a2.emf_base_string + "|" + a2.building_class + "|" + a2.emf_end_use

    a3_0["emf_string"] = a3_0.region + a3_0.emf_base_string + "|" + a3_0.emf_direct_indirect_fuel
    a3_1["emf_string"] = a3_1.region + a3_1.emf_base_string + "|" + a3_1.building_class + "|" + a3_1.emf_direct_indirect_fuel
    a3_2["emf_string"] = a3_2.region + a3_2.emf_base_string + "|" + a3_2.building_class + "|" + a3_2.emf_end_use + "|" + a3_2.emf_direct_indirect_fuel

    a4_0["emf_string"] = a4_0.region + a4_0.emf_base_string + "|" + a4_0.emf_fuel_type
    a4_1["emf_string"] = a4_1.region + a4_1.emf_base_string + "|" + a4_1.building_class + "|" + a4_1.emf_fuel_type
    a4_2["emf_string"] = a4_2.region + a4_2.emf_base_string + "|" + a4_2.building_class + "|" + a4_2.emf_end_use + "|" + a4_2.emf_fuel_type

    # build one data frame with all the aggregations
    ecm_results_emf_aggregation = pd.concat([
        a0[["emf_string", "year", "value"]],
        a1[["emf_string", "year", "value"]],
        a2[["emf_string", "year", "value"]],
        a3_0[["emf_string", "year", "value"]],
        a3_1[["emf_string", "year", "value"]],
        a3_2[["emf_string", "year", "value"]],
        a4_0[["emf_string", "year", "value"]],
        a4_1[["emf_string", "year", "value"]],
        a4_2[["emf_string", "year", "value"]]
        ])

    # create a wide version of the ecm_results_emf_aggregation
    ecm_results_emf_aggregation_wide = ecm_results_emf_aggregation.copy(deep = True)

    ecm_results_emf_aggregation_wide.year =\
            ecm_results_emf_aggregation_wide.year.apply(str) # this is needed so the column names post pivot are strings

    ecm_results_emf_aggregation_wide =\
            ecm_results_emf_aggregation_wide.pivot_table(
                    index = ["emf_string"],
                    columns = ["year"],
                    values = ["value"]
                    )

    ecm_results_emf_aggregation_wide.columns = ecm_results_emf_aggregation_wide.columns.droplevel(0)

    ecm_results_emf_aggregation.reset_index(inplace = True, drop = True)
    ecm_results_emf_aggregation_wide.reset_index(inplace = True, drop = False)

    
    print("outputing EMF aggrgations:")
    print("  " + emf_output_path + "/ecm_results_emf_aggregation.csv")
    ecm_results_emf_aggregation.to_csv(
            path_or_buf = emf_output_path + "/ecm_results_emf_aggregation.csv"
            )
    print("  " + emf_output_path + "/ecm_results_emf_aggregation_wide.csv")
    ecm_results_emf_aggregation_wide.to_csv(
            path_or_buf = emf_output_path + "/ecm_results_emf_aggregation_wide.csv"
            )

    ###########################################################################
    # Baseline aggregations
    print("Baseline Aggregation")

    b1 = baseline[baseline.fuel_type == "other fuel"]
    b2 = baseline[baseline.fuel_type != "other fuel"]

    b1 = b1.merge(
            right = emf_other_fuel_types, 
            how = "left",
            left_on = ["fuel_type", "end_use", "technology_type"],
            right_on = ["scout_split_fuel", "scout_end_use", "scout_technology_type"]
            )

    b2 = b2.merge(
            right = emf_fuel_types, 
            how = "left",
            left_on = ["fuel_type"],
            right_on = ["scout_split_fuel"]
            )

    baseline = pd.concat([b1, b2])


    b0 = baseline\
            .groupby(["region", "emf_CO2_conversion_factor", "emf_base_string", "year"])\
            .agg(value = ("value", "sum"))

    b1 = baseline\
            .groupby(["region", "emf_CO2_conversion_factor", "emf_base_string", "emf_fuel_type", "year"])\
            .agg(value = ("value", "sum"))

    b2 = baseline\
            .groupby(["region", "emf_CO2_conversion_factor", "emf_base_string", "building_class", "emf_fuel_type", "year"])\
            .agg(value = ("value", "sum"))

    b3 = baseline\
            .groupby(["region", "emf_CO2_conversion_factor", "emf_base_string", "building_class", "end_use", "emf_fuel_type", "year"])\
            .agg(value = ("value", "sum"))

    b0.reset_index(inplace = True)
    b1.reset_index(inplace = True)
    b2.reset_index(inplace = True)
    b3.reset_index(inplace = True)

    b0["emf_string"] = b0.region + b0.emf_base_string
    b1["emf_string"] = b1.region + b1.emf_base_string + "|" + b1.emf_fuel_type
    b2["emf_string"] = b2.region + b2.emf_base_string + "|" + b2.building_class + "|" + b2.emf_fuel_type
    b3["emf_string"] = b3.region + b3.emf_base_string + "|" + b3.building_class + "|" + b3.end_use + "|" + b3.emf_fuel_type

    baseline_emf_aggregation = pd.concat( [b0, b1, b2, b3])

    baseline_emf_aggregation["EJ"] = baseline_emf_aggregation["value"] * MMBtu_to_EJ
    baseline_emf_aggregation["CO2"] = np.nan # define the column for CO2

    # merge on the CO2 intensity of electricity.  This merge will result values
    # for all rows.  After the merge we need to set the value for
    # CO2_intensity_of_electricity to 1 for emf_fuel_type <> "Electricity" so
    # that column multiplication can be used later.
    baseline_emf_aggregation =\
            baseline_emf_aggregation\
            .merge(coeffs_emm, on = ["region", "year"])

    baseline_emf_aggregation.loc[baseline_emf_aggregation.emf_fuel_type == "Electricity", "CO2_intensity_of_electricity"] = 1.00

    # CO2 values are:
    baseline_emf_aggregation["CO2"] = \
            baseline_emf_aggregation.EJ *\
            baseline_emf_aggregation.CO2_intensity_of_electricity *\
            baseline_emf_aggregation.emf_CO2_conversion_factor

    # wide version
    baseline_emf_aggregation_wide = baseline_emf_aggregation.copy(deep = True)

    baseline_emf_aggregation_wide.year =\
            baseline_emf_aggregation_wide.year.apply(str) # this is needed so the column names post pivot are strings

    baseline_emf_aggregation_wide =\
            baseline_emf_aggregation_wide.pivot_table(
                    index = ["emf_string"],
                    columns = ["year"],
                    values = ["CO2"]
                    )

    baseline_emf_aggregation_wide.columns = baseline_emf_aggregation_wide.columns.droplevel(0)

    baseline_emf_aggregation.reset_index(inplace = True, drop = True)
    baseline_emf_aggregation_wide.reset_index(inplace = True, drop = False)

    print("Write out baseline aggregation:" +  emf_output_path + "/baseline_emf_aggregation.csv")
    baseline_emf_aggregation.to_csv(
            path_or_buf = emf_output_path + "/baseline_emf_aggregation.csv"
            )
    print("Write out baseline aggregation (wide):" +  emf_output_path + "/baseline_emf_aggregation_wide.csv")
    baseline_emf_aggregation_wide.to_csv(
            path_or_buf = emf_output_path + "/baseline_emf_aggregation_wide.csv"
            )
