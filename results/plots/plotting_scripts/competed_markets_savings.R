################################################################################
###                 Clean Markets and Savings (By Category)                  ###

# Import competed ECM energy, carbon, and cost data
ecm_results <-
  rjson::fromJSON(file = file.path('.', 'results','ecm_results.json'))

# extract the markets and savings data
competed_markets_savings <-
  lapply(ecm_results, getElement, "Markets and Savings (by Category)")

# transform from json structure to a data.frame structure

competed_markets_savings <-
  lapply(competed_markets_savings,
         lapply, lapply, lapply, lapply, lapply,
         data.table::as.data.table)

competed_markets_savings <-
  lapply(competed_markets_savings,
         lapply, lapply, lapply, lapply,
         data.table::rbindlist, idcol = "end_use")

competed_markets_savings <-
  lapply(competed_markets_savings,
         lapply, lapply, lapply,
         data.table::rbindlist,
         idcol = "building_class")

competed_markets_savings <-
  lapply(competed_markets_savings,
         lapply, lapply,
         data.table::rbindlist,
         idcol = "region")

competed_markets_savings <-
  lapply(competed_markets_savings,
         lapply,
         data.table::rbindlist,
         idcol = "variable")

competed_markets_savings <-
  lapply(competed_markets_savings,
         data.table::rbindlist,
         idcol = "adoption_scenario")

competed_markets_savings <-
  data.table::rbindlist(competed_markets_savings, idcol = "ecm")

competed_markets_savings <-
  data.table::melt(competed_markets_savings,
                   id.vars = c("ecm", "adoption_scenario", "region",
                               "building_class", "end_use", "variable"),
                   variable.factor = FALSE,
                   variable.name = "year")

competed_markets_savings

saveRDS(competed_markets_savings,
        file = "./results/plots/competed_markets_savings.rds")

################################################################################
###                               End of File                                ###
################################################################################

