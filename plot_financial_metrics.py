import pandas as pd
import plotly.express as px

fm = pd.read_parquet("./results/plots/financial_metrics.parquet")
fm.sort_values(by = ['ecm', 'variable', 'year'], inplace = True)

fm['facet_row'] = fm["variable"]
fm['facet_row'][fm["variable"] == "Cost of Conserved CO\u2082 ($/MTon CO\u2082 avoided)"] = "Cost of Conserved CO\u2082<br>($/MTon CO\u2082 avoided)"
fm['facet_row'][fm["variable"] == "Cost of Conserved Energy ($/MMBtu saved)"] = "Cost of Conserved Energy<br>($/MMBtu saved)"


fig = px.line(fm
        , x = "year"
        , y = "value"
        , color = "ecm"
        , facet_row = "facet_row")
fig.update_yaxes(matches = None)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.show()
fig.write_html("./results/plots/financial_metrics.html")

agg_fm = fm.groupby(["facet_row", "year"]).value.agg(["mean"])

agg_fm.reset_index(inplace = True)

agg_fm

fig = px.line(agg_fm
        , x = "year"
        , y = "mean"
        , facet_row = "facet_row")
fig.update_yaxes(matches = None)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.show()
fig.write_html("./results/plots/aggregated_financial_metrics.html")
