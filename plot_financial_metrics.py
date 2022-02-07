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


fig = px.line(fm
        , x = "year"
        , y = "value"
        , color = "ecm"
        , facet_row = "facet_row")
fig.update_yaxes(matches = None)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#fig.show()
print("Writing './results/plots/financial_metrics.html")
fig.write_html("./results/plots/financial_metrics.html")


# aggregate data and generate the plot
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
print("Writing './results/plots/aggregated_financial_metrics.html")
fig.write_html("./results/plots/aggregated_financial_metrics.html")
