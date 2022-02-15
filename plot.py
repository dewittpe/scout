import subprocess
from subprocess import Popen
from subprocess import PIPE
import os

################################################################################
def mtime(p):
    if os.path.isfile(p):
        return os.path.getmtime(p)
    else:
        return 0

################################################################################
# Check if ecm_prep.py and/or run.py need to be evaluated.

if not os.path.isfile("./supporting_data/ecm_prep.json"):
    print("./supporting_data/ecm_prep.json does not exist")
    exit(1)

ecm_prep_json_mtime = os.path.getmtime("./supporting_data/ecm_prep.json")

if ecm_prep_json_mtime < os.path.getmtime("./ecm_prep.py"):
    print("rerun ecm_prep.py")
    exit(1)

if not os.path.isfile("./results/ecm_results.json"):
    print("./supporting_data/ecm_results.json does not exist. evaluate run.py")
    exit(1)

ecm_results_json_mtime = os.path.getmtime("./results/ecm_results.json")

if ( (ecm_results_json_mtime < ecm_prep_json_mtime) |\
     (ecm_results_json_mtime < os.path.getmtime("./run.py")) ):
    print("rerun ecm_prep.py")
    exit(1)

################################################################################
# Translate the JSON to DataFrames and save as parquet
fmdpmt  = mtime("./plot_financial_metrics_data_prep.py")
cmsdpmt = mtime("./plot_competed_market_savings_data_prep.py")
umsdpmt = mtime("./plot_uncompeted_market_savings_data_prep.py")

fm_parquet_mt  = mtime('./results/plots/financial_metrics.parquet')
cms_parquet_mt = mtime('./results/plots/competed_market_savings.parquet')
ums_parquet_mt = mtime('./results/plots/uncompeted_market_savings.parquet')

# create output directories, if needed
os.makedirs('./results/plots/financial_metrics/each_ecm', exist_ok = True)
os.makedirs('./results/plots/cost_effective_carbon_savings', exist_ok = True)
os.makedirs('./results/plots/cost_effective_cost_savings', exist_ok = True)
os.makedirs('./results/plots/cost_effective_energy_savings', exist_ok = True)
os.makedirs('./results/plots/total_carbon_savings', exist_ok = True)
os.makedirs('./results/plots/total_cost_savings', exist_ok = True)
os.makedirs('./results/plots/total_energy_savings', exist_ok = True)
os.makedirs('./results/plots/total_carbon', exist_ok = True)
os.makedirs('./results/plots/total_cost', exist_ok = True)
os.makedirs('./results/plots/total_energy', exist_ok = True)

# empty command list
cmd_list = []
if ((fm_parquet_mt < fmdpmt) | (fm_parquet_mt < ecm_results_json_mtime)):
    print("financial_metrics.parquet will be updated")
    cmd_list.append(['python', './plot_financial_metrics_data_prep.py'])
else:
    print("financial_metrics.parquet is up to date.")

if ((cms_parquet_mt < cmsdpmt) | (cms_parquet_mt < ecm_results_json_mtime)):
    print("competed_market_savings.parquet will be updated")
    cmd_list.append(['python', './plot_competed_market_savings_data_prep.py'])
else:
    print("competed_market_savings.parquet is up to date.")

if ((ums_parquet_mt < umsdpmt) | (ums_parquet_mt < ecm_prep_json_mtime)):
    print("uncompeted_market_savings.parquet will be updated")
    cmd_list.append(['python', './plot_uncompeted_market_savings_data_prep.py'])
else:
    print("uncompeted_market_savings.parquet is up to date.")

if len(cmd_list) > 0:
    proc_list = [Popen(cmd, stdout = PIPE, stderr = PIPE) for cmd in cmd_list]
    for proc in proc_list:
        proc.wait()

################################################################################
# Build command list for plots
cmd_list = []

# get the mtime for the parquet files again, incase they were updated above
fm_parquet_mt  = mtime('./results/plots/financial_metrics.parquet')
cms_parquet_mt = mtime('./results/plots/competed_market_savings.parquet')
ums_parquet_mt = mtime('./results/plots/uncompeted_market_savings.parquet')

# Financial Metric Plots
fm_mt = mtime("./results/plots/.financial_metrics")

if ((fm_mt < fm_parquet_mt) | (fm_mt < os.path.getmtime("plot_financial_metrics.py"))):
    print("Financial metric plots will be updated.")
    cmd_list.append(['python', './plot_financial_metrics.py'])
else:
    print("Financial metric plots are up to date.")

# Cost Effective Savings
for cce in ['carbon', 'cost', 'energy']:
    mt = mtime('./results/plots/.cost_effective_' + cce + '_savings')
    if ((mt < mtime('./plot_cost_effective.py')) | (mt < cms_parquet_mt) | (mt < fm_parquet_mt)):
        print("Cost Effective " + cce + " Savings will be updated.")
        cmd_list.append(['python', './plot_cost_effective.py', cce])
    else:
        print("Cost Effective " + cce + " Savings is up to date.")

# Total Savings
for cce in ['carbon', 'cost', 'energy']:
    mt = mtime('./results/plots/.total_' + cce + '_savings')
    if ((mt < mtime('./plot_total_savings.py')) | (mt < cms_parquet_mt)):
        print("Total " + cce + " Savings will be updated.")
        cmd_list.append(['python', './plot_total_savings.py', cce])
    else:
        print("Total " + cce + " Savings is up to date.")

# Totals
for cce in ['carbon', 'cost', 'energy']:
    mt = mtime('./results/plots/.total_' + cce)
    if ((mt < mtime('./plot_cost_effective.py')) | (mt < cms_parquet_mt) | (mt < ums_parquet_mt)):
        print("Total " + cce + " will be updated.")
        cmd_list.append(['python', './plot_total.py', cce])
    else:
        print("Total " + cce + " is up to date.")

if len(cmd_list) > 0:
    proc_list = [Popen(cmd, stdout = PIPE, stderr = PIPE) for cmd in cmd_list]
    for proc in proc_list:
        proc.wait()

################################################################################
# End of File                     End of File                      End of File #
################################################################################

