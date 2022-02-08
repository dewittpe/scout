import pandas as pd
import plotly.express as px

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
ms = ms[ms["ecc"].isin(["carbon"])]

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
                "value": "CO\u2082 Emissions (MMTons)",
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
    fm = ecm.replace(" ", "_")
    print("Writing: ./results/plots/total_co2/" + fm + ".html")
    fig.write_html("./results/plots/total_co2/" + fm + ".html")

