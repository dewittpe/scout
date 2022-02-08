import sys
import pandas as pd
import plotly.express as px

# Variable of Interest and paths
arg = str(sys.argv[1])

if arg == "carbon":
    VOI = "CO\u2082 Emissions (MMTons)"
    plot_path = "./results/plots/total_carbon/"
elif arg == "cost":
    VOI = "Cost (USD)"
    plot_path = "./results/plots/total_cost/"
elif arg == "energy":
    VOI = "Energy Use (MMBtu)"
    plot_path = "./results/plots/total_energy/"
else:
    print("unknown arg value")
    exit(1)

# aggregate
def unique_strings(l):
    list_set = set(l)
    ul = (list(list_set))
    return '; '.join(ul)

# read in data
cms = pd.read_parquet("./results/plots/competed_market_savings.parquet")
ums = pd.read_parquet("./results/plots/uncompeted_market_savings.parquet")

cms.sort_values(by = ['ecm', 'variable', 'year'], inplace = True)
ums.sort_values(by = ['ecm', 'year'], inplace = True)

ms = cms.append(ums, sort = True)

ms = ms[ms["results_scenario"].isin(["baseline", "efficient"])]
ms = ms[ms["ecc"].isin([arg])]

ms = ms.groupby(["adoption_scenario", "ecm", "competed", "results_scenario", "year"])\
        .agg({
            "value": "sum",
            "building_class" : unique_strings,
            "region" : unique_strings,
            "end_use" : unique_strings
            })
ms.reset_index(inplace = True)

for ecm in set(ms["ecm"]):
    fig = px.scatter(
            ms[ms["ecm"] == ecm],
            x = "year",
            y = "value",
            color = "results_scenario",
            symbol = "competed",
            facet_col = "adoption_scenario",
            labels = {
                "year": "Year",
                "value": VOI,
                "results_scenario": "Results Scenario",
                "competed": "Competed"
                },
            title = "ECM: " + ecm + "<br><sup>Building Class: " +\
                    unique_strings(ms.loc[ms["ecm"] == ecm, "building_class"]) +\
                    " | Region: " +\
                    unique_strings(ms.loc[ms["ecm"] == ecm, "region"]) +\
                    " | End Use: " +\
                    unique_strings(ms.loc[ms["ecm"] == ecm, "end_use"]) +\
                    "</sup>"
            )
    fig.update_traces(mode = "lines+markers")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    print("Writing: " + plot_path + ecm + ".html")
    fig.write_html(plot_path + ecm + ".html")


# create the java script needed for a dropdown list of the ecms
with open(plot_path + 'each_ecm.js', 'w') as f:
    f.write('var total_' + arg + '_ecm_select_list = document.createElement("select");\n')
    f.write('var total_' + arg + '_ecms =' + "['--', '" + "', '".join(sorted(set(list(ms["ecm"])))) + "']\n")
    f.write('total_' + arg + '_ecm_select_list.setAttribute("id", "total_' + arg + '_ecm_select");\n')
    f.write('total_' + arg + '_ecm_select_list.setAttribute("onchange", "if (this.selectedIndex) get_total_' + arg + '_ecm();");\n')
    f.write('document.getElementById("total_' + arg + '_ecms_div").appendChild(total_' + arg + '_ecm_select_list);\n')
    f.write('for (var i = 0; i < total_' + arg + '_ecms.length; i++) {\n')
    f.write('\tvar option = document.createElement("option");\n')
    f.write('\toption.setAttribute("value", total_' + arg + '_ecms[i]);\n')
    f.write('\toption.text = total_' + arg + '_ecms[i];\n')
    f.write('\ttotal_' + arg + '_ecm_select_list.appendChild(option);\n')
    f.write('}')

