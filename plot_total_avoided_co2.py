import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# read in data
cms = pd.read_parquet("./results/plots/competed_market_savings.parquet")
cms.sort_values(by = ['ecm', 'variable', 'year'], inplace = True)

# subset to avoided CO2
cms = cms[cms["variable"] == "Avoided CO\u2082 Emissions (MMTons)"]


# get total for each year and cummulative
total = \
        cms\
        .groupby(["adoption_scenario", "variable", "year"])\
        .agg({"value":"sum"})\
        .reset_index()
total2 = pd.DataFrame.copy(total)
total2["value"] = total2.value.cumsum()

# summary by region
cms_by_region =\
        cms.groupby(["adoption_scenario", "variable", "year", "region"]).agg({"value":"sum"})
cms_by_region.reset_index(inplace = True)


# summary by building_class
cms_by_building_class =\
        cms.groupby(["adoption_scenario", "variable", "year", "building_class"]).agg({"value":"sum"})
cms_by_building_class.reset_index(inplace = True)

# summary by end_use
cms_by_end_use =\
        cms.groupby(["adoption_scenario", "variable", "year", "end_use"]).agg({"value":"sum"})
cms_by_end_use.reset_index(inplace = True)

# add totals to the summaries

total["region"] = "Annual Total"
total2["region"] = "Cumulative Total"
cms_by_region = cms_by_region.append(total, sort = True).append(total2, sort = True)
total.drop(columns = ["region"])
total2.drop(columns = ["region"])

total["building_class"] = "Annual Total"
total2["building_class"] = "Cumulative Total"
cms_by_building_class = cms_by_building_class.append(total, sort = True).append(total2, sort = True)
total.drop(columns = ["building_class"])
total2.drop(columns = ["building_class"])

total["end_use"] = "Annual Total"
total2["end_use"] = "Cumulative Total"
cms_by_end_use = cms_by_end_use.append(total, sort = True).append(total2, sort = True)
total.drop(columns = ["end_use"])
total2.drop(columns = ["end_use"])


# figures
fig = px.scatter(
        cms_by_region,
        x = "year",
        y = "value",
        color = "region",
        facet_col = "adoption_scenario")
fig.update_traces(mode = "lines+markers")
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
print("Writing  ./results/plots/total_avoided_co2_by_region.html")
fig.write_html("./results/plots/total_avoided_co2_by_region.html")

fig = px.scatter(
        cms_by_building_class,
        x = "year",
        y = "value",
        color = "building_class",
        facet_col = "adoption_scenario")
fig.update_traces(mode = "lines+markers")
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
print("Writing  ./results/plots/total_avoided_co2_by_building_class.html")
fig.write_html("./results/plots/total_avoided_co2_by_building_class.html")

fig = px.scatter(
        cms_by_end_use,
        x = "year",
        y = "value",
        color = "end_use",
        facet_col = "adoption_scenario")
fig.update_traces(mode = "lines+markers")
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
print("Writing  ./results/plots/total_avoided_co2_by_end_use.html")
fig.write_html("./results/plots/total_avoided_co2_by_end_use.html")


