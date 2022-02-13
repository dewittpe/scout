import subprocess
from subprocess import Popen
from subprocess import PIPE
import os

################################################################################
# Check if ecm_prep.py and/or run.py need to be evaluated.

if not os.path.exists("./supporting_data/ecm_prep.json"):
    print("./supporting_data/ecm_prep.json does not exist")
    exit(1)

ecm_prep_json_mtime = os.path.getmtime("./supporting_data/ecm_prep.json")

if ecm_prep_json_mtime < os.path.getmtime("./ecm_prep.py"):
    print("rerun ecm_prep.py")
    exit(1)

if not os.path.exists("./results/ecm_results.json"):
    print("./supporting_data/ecm_results.json does not exist. evaluate run.py")
    exit(1)

ecm_results_json_mtime = os.path.getmtime("./results/ecm_results.json")

if ( (ecm_results_json_mtime < ecm_prep_json_mtime) |\
     (ecm_results_json_mtime < os.path.getmtime("./run.py")) ):
    print("rerun ecm_prep.py")
    exit(1)

################################################################################
# Translate the JSON to DataFrames and save as parquet
fmdpmt  = os.path.getmtime("./plot_financial_metrics_data_prep.py")
cmsdpmt = os.path.getmtime("./plot_competed_market_savings_data_prep.py")
umsdpmt = os.path.getmtime("./plot_uncompeted_market_savings_data_prep.py")

if os.path.exists("./results/plots/financial_metrics.parquet"):
    fm_parquet_mt = os.path.getmtime('./results/plots/financial_metrics.parquet')
else:
    fm_parquet_mt = 0

if os.path.exists("./results/plots/competed_market_savings.parquet"):
    cms_parquet_mt = os.path.getmtime('./results/plots/competed_market_savings.parquet')
else:
    cms_parquet_mt = 0

if os.path.exists("./results/plots/uncompeted_market_savings.parquet"):
    ums_parquet_mt = os.path.getmtime('./results/plots/uncompeted_market_savings.parquet')
else:
    ums_parquet_mt = 0

cmd_list = []
if fm_parquet_mt < fmdpmt:
    print("financial_metrics.parquet does need updating")
    cmd_list.append(['python', './plot_financial_metrics_data_prep.py'])
else:
    print("financial_metrics.parquet does not need updating")

if cms_parquet_mt < cmsdpmt:
    print("competed_market_savings.parquet does need updating")
    cmd_list.append(['python', './plot_competed_market_savings_data_prep.py'])
else:
    print("competed_market_savings.parquet does not need updating")

if ums_parquet_mt < umsdpmt:
    print("uncompeted_market_savings.parquet does need updating")
    cmd_list.append(['python', './plot_uncompeted_market_savings_data_prep.py'])
else:
    print("uncompeted_market_savings.parquet does not need updating")

if len(cmd_list) > 0:
    proc_list = [Popen(cmd, stdout = PIPE, stderr = PIPE) for cmd in cmd_list]
    for proc in proc_list:
        proc.wait()


#subprocess.run(['python', './plot_financial_metrics_data_prep.py'])
#subprocess.run(['python', './plot_uncompeted_market_savings_data_prep.py'])
#subprocess.run(['python', './plot_competed_market_savings_data_prep.py'])

# Generate "financial metrics" graphics
#subprocess.run(['python', './plot_financial_metrics.py'])

# Generate "cost effective" graphics
#subprocess.run(['python', './plot_cost_effective.py', 'carbon'])
#subprocess.run(['python', './plot_cost_effective.py', 'cost'])
#subprocess.run(['python', './plot_cost_effective.py', 'energy'])

# Generate "total savings" graphics
#subprocess.run(['python', './plot_total_savings.py', 'carbon'])
#subprocess.run(['python', './plot_total_savings.py', 'cost'])
#subprocess.run(['python', './plot_total_savings.py', 'energy'])

# Generate "total" graphics
#subprocess.run(['python', './plot_total.py', 'carbon'])
#subprocess.run(['python', './plot_total.py', 'cost'])
#subprocess.run(['python', './plot_total.py', 'energy'])

################################################################################
# End of File                     End of File                      End of File #
################################################################################

