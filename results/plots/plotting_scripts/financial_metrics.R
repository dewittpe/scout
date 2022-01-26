################################################################################
# Import competed ECM energy, carbon, and cost data
ecm_results <-
  rjson::fromJSON(file = file.path('.', 'results','ecm_results.json'))

################################################################################
# extract the financial_metrics
financial_metrics <- lapply(ecm_results, getElement, "Financial Metrics")

################################################################################
# transfrom from the json form to a data.table
financial_metrics <-
  lapply(financial_metrics, lapply, data.table::as.data.table)

financial_metrics <-
  lapply(financial_metrics,
         data.table::rbindlist,
         idcol = "variable")

financial_metrics <-
  data.table::rbindlist(financial_metrics, idcol = "ecm")

financial_metrics <-
  data.table::melt(financial_metrics,
                   id.vars = c("ecm", "variable"),
                   variable.factor = FALSE,
                   variable.name = "year")

################################################################################
# storage modes, extra colums
financial_metrics[, year := as.integer(year)]

saveRDS(financial_metrics, file = "./results/plots/financial_metrics.rds")

################################################################################
###                               End of File                                ###
################################################################################

