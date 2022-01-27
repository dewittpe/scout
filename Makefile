plotdata  = ./results/plots/competed_markets_savings.rds
plotdata += ./results/plots/financial_metrics.rds
plotdata += ./results/plots/on_site_generation.rds
plotdata += ./results/plots/uncompeted_markets_savings.rds

all : $(plotdata)


./results/plots/competed_markets_savings.rds : ./results/plots/plotting_scripts/competed_markets_savings.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/financial_metrics.rds : ./results/plots/plotting_scripts/financial_metrics.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/on_site_generation.rds : ./results/plots/plotting_scripts/on_site_generation.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/uncompeted_markets_savings.rds : ./results/plots/plotting_scripts/uncompeted_markets_savings.R ./supporting_data/ecm_prep.json
	R CMD BATCH --vanilla $<

clear_rds :
	rm -f $(plotdata)
