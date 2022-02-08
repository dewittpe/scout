plotting_datasets  = ./results/plots/financial_metrics.parquet
plotting_datasets += ./results/plots/competed_market_savings.parquet
plotting_datasets += ./results/plots/uncompeted_market_savings.parquet

all: $(plotting_datasets)

./supporting_data/ecm_prep.json : ./ecm_prep.py
	python $<

./results/ecm_results.json : ./run.py
	python $<

./results/plots/financial_metrics.parquet : plot_financial_metrics_data_prep.py ./results/ecm_results.json
	python $<

./results/plots/competed_market_savings.parquet : plot_competed_market_savings_data_prep.py ./results/ecm_results.json
	python $<

./results/plots/uncompeted_market_savings.parquet : plot_uncompeted_market_savings_data_prep.py ./supporting_data/ecm_prep.json
	python $<

clean:
	/bin/rm -f ./results/ecm_results.json
	/bin/rm -f ./supporting_data/ecm_prep.json
