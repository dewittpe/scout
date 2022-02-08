import pandas as pd
import plotly.express as px

fm = pd.read_parquet("./results/plots/financial_metrics.parquet")
fm.sort_values(by = ['ecm', 'variable', 'year'], inplace = True)


# copy the variable column to be used as a facetting value
fm['facet_row'] = fm["variable"]

fm.loc[fm["variable"] == "Cost of Conserved CO\u2082 ($/MTon CO\u2082 avoided)"
        , "facet_row"] =\
                "Cost of Conserved CO\u2082<br>($/MTon CO\u2082 avoided)"

fm.loc[fm["variable"] == "Cost of Conserved Energy ($/MMBtu saved)"
        , "facet_row"] =\
                "Cost of Conserved Energy<br>($/MMBtu saved)"

# aggregate data and generate an aggregate plot
agg_fm = fm.groupby(["facet_row", "year"]).value.agg(["mean"])

agg_fm.reset_index(inplace = True)

agg_fm

fig = px.line(agg_fm
        , x = "year"
        , y = "mean"
        , facet_row = "facet_row")
fig.update_yaxes(matches = None)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#fig.show()
print( "Writing ./results/plots/financial_metrics/aggregated.html")
fig.write_html("./results/plots/financial_metrics/aggregated.html")

# plot showing _all_ ecms
fig = px.line(fm
        , x = "year"
        , y = "value"
        , color = "ecm"
        , facet_row = "facet_row")
fig.update_yaxes(matches = None)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
print("Writing './results/plots/financial_metrics/all_ecms.html")
fig.write_html("./results/plots/financial_metrics/all_ecms.html")

# create a plot for each of the ecms
for ecm in set(list(fm["ecm"])):
    fig = px.line(fm[fm["ecm"] == ecm]
            , x = "year"
            , y = "value"
            , title = ecm
            , facet_row = "facet_row")
    fig.update_yaxes(matches = None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    print("Writing './results/plots/financial_metrics/" + ecm + ".html")
    fig.write_html("./results/plots/financial_metrics/" + ecm + ".html")
