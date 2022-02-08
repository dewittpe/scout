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
        , title = "Aggregated"
        , facet_row = "facet_row")
fig.update_yaxes(matches = None, exponentformat = "e")
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
fig.update_yaxes(matches = None, exponentformat = "e")
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
    fig.update_yaxes(matches = None, exponentformat = "e")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    print("Writing './results/plots/financial_metrics/each_ecm/" + ecm + ".html")
    fig.write_html("./results/plots/financial_metrics/each_ecm/" + ecm + ".html")

# create the java script needed for a dropdown list of the ecms
with open('./results/plots/financial_metrics/each_ecm.js', 'w') as f:
    f.write('var all_fm_ecm_select_list = document.createElement("select");\n')
    f.write('var all_fm_ecms =' + "['--', '" + "', '".join(sorted(set(list(fm["ecm"])))) + "']\n")
    f.write('all_fm_ecm_select_list.setAttribute("id", "all_fm_ecm_select");\n')
    f.write('all_fm_ecm_select_list.setAttribute("onchange", "if (this.selectedIndex) get_fm_ecm();");\n')
    f.write('document.getElementById("all_fm_ecms_div").appendChild(all_fm_ecm_select_list);\n')
    f.write('for (var i = 0; i < all_fm_ecms.length; i++) {\n')
    f.write('\tvar option = document.createElement("option");\n')
    f.write('\toption.setAttribute("value", all_fm_ecms[i]);\n')
    f.write('\toption.text = all_fm_ecms[i];\n')
    f.write('\tall_fm_ecm_select_list.appendChild(option);\n')
    f.write('}')

