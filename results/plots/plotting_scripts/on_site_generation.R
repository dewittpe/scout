################################################################################
# Import competed ECM energy, carbon, and cost data
ecm_results <-
  rjson::fromJSON(file = file.path('.', 'results','ecm_results.json'))

################################################################################
# focus on the on site generation data
on_site_generation <- ecm_results[["On-site Generation"]]
on_site_generation <- lapply(on_site_generation, getElement, "By Category")

################################################################################
# transfrom from json fromat to data.table
on_site_generation <-
  lapply(on_site_generation, lapply, lapply, data.table::as.data.table)

on_site_generation <-
  lapply(on_site_generation, lapply,
         data.table::rbindlist, idcol = "building_type")

on_site_generation <-
  lapply(on_site_generation,
         data.table::rbindlist, idcol = "region")

on_site_generation <-
  data.table::rbindlist(on_site_generation, idcol = "variable")

on_site_generation <-
  data.table::melt(on_site_generation,
                   id.vars = c("variable", "region", "building_type"),
                   variable.factor = FALSE,
                   variable.name = "year")

################################################################################
# storage modes, extra colums
on_site_generation[, year := as.integer(year)]

saveRDS(on_site_generation, file = "./results/plots/on_site_generation.rds")

################################################################################
###                               End of File                                ###
################################################################################

