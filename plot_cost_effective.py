import sys
import pandas as pd
import plotly.express as px

# Variable of Interest and paths
arg = str(sys.argv[1])

if arg == "carbon":
    VOI = "Avoided CO\u2082 Emissions (MMTons)"
    plot_path = "./results/plots/cost_effective_carbon_savings/"
elif arg == "cost":
    VOI = "Energy Cost Savings (USD)"
    plot_path = "./results/plots/cost_effective_operation_cost_savings/"
elif arg == "energy":
    VOI = "Energy Savings (MMBtu)"
    plot_path = "./results/plots/cost_effective_energy_savings/"
else:
    print("unknown arg value")
    exit(1)


# aggregate by building type
def unique_strings(l):
    list_set = set(l)
    ul = (list(list_set))
    return '; '.join(ul)

# data import
fm = pd.read_parquet("./results/plots/financial_metrics.parquet")
cms = pd.read_parquet("./results/plots/competed_market_savings.parquet")

fm.sort_values(by = ['ecm', 'variable', 'year'], inplace = True)
cms.sort_values(by = ['ecm', 'variable', 'year'], inplace = True)

# subset
set(list(cms["variable"]))
cms = cms[cms["variable"] == VOI]

# copy the variable column to be used as a facetting value
fm['facet_row'] = fm["variable"]

fm.loc[fm["variable"] == "Cost of Conserved CO\u2082 ($/MTon CO\u2082 avoided)"
        , "facet_row"] =\
                "Cost of Conserved CO\u2082<br>($/MTon CO\u2082 avoided)"

fm.loc[fm["variable"] == "Cost of Conserved Energy ($/MMBtu saved)"
        , "facet_row"] =\
                "Cost of Conserved Energy<br>($/MMBtu saved)"

# aggregate
cms =\
    cms.groupby(["adoption_scenario", "ecm", "variable", "year"])\
            .agg({
                "value": "sum",
                "building_class" : unique_strings,
                "region" : unique_strings,
                "end_use" : unique_strings
                  })

cms.reset_index(inplace = True)

cms = \
    pd.pivot_table(cms,
            values = "value",
            index = ["adoption_scenario", "ecm", "building_class", "end_use",
                "year"],
            columns = ["variable"])

cms.reset_index(inplace = True)

plot_data = cms.merge(fm, how = "left", on = ["ecm", "year"])
plot_data["year"] = plot_data["year"].astype(str).astype(int)


def plot_year(yr = 2022):
    fig = px.scatter(
            plot_data[(plot_data["year"] == yr)]
            , x = VOI
            , y = "value"
            , symbol = "building_class"
            , color = "end_use"
            , facet_col = "adoption_scenario"
            , facet_row = "facet_row"
            , title = "Calendar Year " + str(yr)
            , hover_data = {
                "ecm": True,
                VOI : True,
                "value": True,
                "end_use": True,
                "building_class": True
                }
            )
    fig.update_yaxes(matches = None, exponentformat = "e")
    fig.update_xaxes(exponentformat = "e")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return(fig)

yr = min(plot_data["year"])
while (yr <= max(plot_data["year"])):
    plot_file = plot_path + str(yr) + ".html"
    print("Writing " + plot_file)
    plot_year(yr = yr).write_html(plot_file)
    yr = yr + 1



