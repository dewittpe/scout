plotdata  = ./results/plots/competed_markets_savings.rds
plotdata += ./results/plots/financial_metrics.rds
plotdata += ./results/plots/on_site_generation.rds
plotdata += ./results/plots/uncompeted_markets_savings.rds

all : $(plotdata) ./results/plots/input_data_eda.Rout

./supporting_data/ecm_prep.json : ecm_prep.py
	python ecm_prep.py

./results/ecm_results.json : ./supporting_data/ecm_prep.json run.py plots.R
	python run.py
	Rscript plots.R

./results/plots/competed_markets_savings.rds : ./results/plots/plotting_scripts/competed_markets_savings.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/financial_metrics.rds : ./results/plots/plotting_scripts/financial_metrics.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/on_site_generation.rds : ./results/plots/plotting_scripts/on_site_generation.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/uncompeted_markets_savings.rds : ./results/plots/plotting_scripts/uncompeted_markets_savings.R ./supporting_data/ecm_prep.json
	R CMD BATCH --vanilla $<

./results/plots/input_data_eda.Rout : ./results/plots/plotting_scripts/input_data_eda.R $(plotdata) ./results/ecm_results.json
	R CMD BATCH --vanilla $< $@

clean :
	rm -f $(plotdata)
	rm -f ./supporting_data/ecm_prep.json
	rm -f ./results/ecm_results.json
