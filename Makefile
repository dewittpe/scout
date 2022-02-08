plotting_datasets  = ./results/plots/financial_metrics.parquet
plotting_datasets += ./results/plots/competed_market_savings.parquet
plotting_datasets += ./results/plots/uncompeted_market_savings.parquet

plots  = ./results/plots/.financial_metrics
plots += ./results/plots/.cost_effective_avoided_co2
plots += ./results/plots/.total_avoided_co2
plots += ./results/plots/.total_co2

all: $(plots)

################################################################################
# Recipes for ECM prep and results -- uncompeted and competed

./supporting_data/ecm_prep.json : ./ecm_prep.py
	python $<

./results/ecm_results.json : ./run.py ./supporting_data/ecm_prep.json
	python $<

################################################################################
# Extract results of the json and build the needed data sets for plotting
#
./results/plots/financial_metrics.parquet : plot_financial_metrics_data_prep.py ./results/ecm_results.json
	python $<

./results/plots/competed_market_savings.parquet : plot_competed_market_savings_data_prep.py ./results/ecm_results.json
	python $<

./results/plots/uncompeted_market_savings.parquet : plot_uncompeted_market_savings_data_prep.py ./supporting_data/ecm_prep.json
	python $<

################################################################################
# Plotting Recipes

./results/plots/.financial_metrics : plot_financial_metrics.py ./results/plots/financial_metrics.parquet
	mkdir -p ./results/plots/financial_metrics
	python $<
	@touch $@

./results/plots/.cost_effective_avoided_co2 : plot_cost_effective_avoided_co2.py ./results/plots/financial_metrics.parquet ./results/plots/competed_market_savings.parquet
	mkdir -p ./results/plots/cost_effective_avoided_co2
	python $<
	@touch $@

./results/plots/.total_avoided_co2 : plot_total_avoided_co2.py ./results/plots/competed_market_savings.parquet
	mkdir -p ./results/plots/total_avoided_co2
	python $<
	@touch $@

./results/plots/.total_co2 : plot_total_co2.py ./results/plots/competed_market_savings.parquet ./results/plots/uncompeted_market_savings.parquet
	mkdir -p ./results/plots/total_co2
	python $<
	@touch $@

################################################################################
clean:
	/bin/rm -f ./results/ecm_results.json
	/bin/rm -f ./supporting_data/ecm_prep.json
	/bin/rm -f $(plotting_datasets)
	/bin/rm -f $(plots)
