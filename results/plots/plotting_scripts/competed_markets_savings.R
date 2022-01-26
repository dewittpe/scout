################################################################################
# Import competed ECM energy, carbon, and cost data
ecm_results <-
  rjson::fromJSON(file = file.path('.', 'results','ecm_results.json'))

################################################################################
# extract the markets and savings data
competed_markets_savings <-
  lapply(ecm_results, getElement, "Markets and Savings (by Category)")

################################################################################
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

################################################################################
# storage modes, extra colums
competed_markets_savings[, year := as.integer(year)]

# Simplify end uses
competed_markets_savings[, end_use2 := end_use]

competed_markets_savings[
  end_use %in% c("Cooling (Equip.)", "Heating (Equip.)", "Ventilation"),
  end_use2 := "HVAC"]

competed_markets_savings[
  end_use %in% c("Cooling (Env.)", "Heating (Env.)"),
  end_use2 := "Envelope"]

competed_markets_savings[
  end_use %in% c("Computers and Electronics"),
  end_use2 := "Electronics"]

competed_markets_savings[
  , end_use2 := factor(end_use2,
                       levels = c('HVAC', 'Envelope', 'Lighting',
                                  'Water Heating', 'Refrigeration',
                                  'Cooking', 'Electronics', 'Other'))]

################################################################################
# save the wanted objects as .rds files
saveRDS(competed_markets_savings,
        file = "./results/plots/competed_markets_savings.rds")

################################################################################
###                               End of File                                ###
################################################################################

