plotdata  = ./results/plots/competed_markets_savings.rds
plotdata += ./results/plots/financial_metrics.rds

all : $(plotdata)


./results/plots/competed_markets_savings.rds : ./results/plots/plotting_scripts/competed_markets_savings.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<

./results/plots/financial_metrics.rds : ./results/plots/plotting_scripts/financial_metrics.R ./results/ecm_results.json
	R CMD BATCH --vanilla $<
