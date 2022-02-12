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

# create a plot for each ecm with a facet for adoption_scenario
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
            title = ecm + "<br><sup>Building Class: " +\
                    unique_strings(ms.loc[ms["ecm"] == ecm, "building_class"]) +\
                    " | Region: " +\
                    unique_strings(ms.loc[ms["ecm"] == ecm, "region"]) +\
                    " | End Use: " +\
                    unique_strings(ms.loc[ms["ecm"] == ecm, "end_use"]) +\
                    "</sup>"
            )
    fig.update_yaxes(exponentformat = "e")
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

# Create a massive plot, one for each adoption_scenario with a facet for each
# ecm

import plotly.graph_objects as go
from plotly.subplots import make_subplots

unique_ecms = list(set(list(ms["ecm"])))
unique_ecms.sort()

ecm_titles = []
for ecm in unique_ecms:
    ecm_titles.append(ecm + "<br><sup>Building Class: " +\
            unique_strings(ms.loc[ms["ecm"] == ecm, "building_class"]) +\
            " <br> Region: " +\
            unique_strings(ms.loc[ms["ecm"] == ecm, "region"]) +\
            " <br> End Use: " +\
            unique_strings(ms.loc[ms["ecm"] == ecm, "end_use"]) +\
            "</sup>")

fig = make_subplots(
        cols = 4,
        rows = round(len(unique_ecms) / 4 + 1),
        subplot_titles = ecm_titles
        )
row = 1
col = 1
for ecm in unique_ecms:
    d = ms[(ms["adoption_scenario"] == "Max adoption potential") &
           (ms["ecm"] == ecm)]
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Competed")],
                y = d["value"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Competed")],
                name = "baseline; competed",
                line_color = "black",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Uncompeted")],
                y = d["value"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Uncompeted")],
                name = "baseline; uncompeted",
                line_color = "red",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Competed")],
                y = d["value"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Competed")],
                name = "efficient; competed",
                line_color = "blue",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Uncompeted")],
                y = d["value"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Uncompeted")],
                name = "efficient; uncompeted",
                line_color = "green",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.update_yaxes(exponentformat = "e", row = row, col = col)
    col = col + 1
    if (col > 4):
        col = 1
        row = row + 1

fig.update_layout(height = 1600 * 7, width = 1600, yaxis = dict(exponentformat = 'e'))
print("Writing: " + plot_path + "_MAP.html")
fig.write_html(plot_path + "_MAP.html")


fig = make_subplots(
        cols = 4,
        rows = round(len(unique_ecms) / 4 + 1),
        subplot_titles = ecm_titles
        )
row = 1
col = 1
for ecm in unique_ecms:
    d = ms[(ms["adoption_scenario"] == "Technical potential") &
           (ms["ecm"] == ecm)]
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Competed")],
                y = d["value"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Competed")],
                name = "baseline; competed",
                line_color = "black",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Uncompeted")],
                y = d["value"][(d["results_scenario"] == "baseline") &
                      (d["competed"] == "Uncompeted")],
                name = "baseline; uncompeted",
                line_color = "red",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Competed")],
                y = d["value"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Competed")],
                name = "efficient; competed",
                line_color = "blue",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    fig.add_trace(
            go.Scatter(
                x = d["year"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Uncompeted")],
                y = d["value"][(d["results_scenario"] == "efficient") &
                      (d["competed"] == "Uncompeted")],
                name = "efficient; uncompeted",
                line_color = "green",
                legendgroup = 'group1',
                showlegend = (row + col == 2)
                ),
        row = row, col = col)
    col = col + 1
    if (col > 4):
        col = 1
        row = row + 1

fig.update_layout(height = 1600 * 7, width = 1600)
print("Writing: " + plot_path + "_TP.html")
fig.write_html(plot_path + "_TP.html")
