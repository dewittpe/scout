
################################################################################
###                               JSON Imports                               ###
################################################################################

# Import uncompleted ECM energy, carbon, and cost data
ecm_prep <-
  rjson::fromJSON(file = file.path('.', 'supporting_data','ecm_prep.json'))

################################################################################
###                              Clean ECM Prep                              ###

# Inspection of the ecm_prep object shows that one of the elements is "name".
# Since the ecm_prep object has no names we will extract the name and assign it
# to the list accordingly.  This will make use of this object easier.
# Deletion of the name element is done to reduce redundancy.
for(i in seq_along(ecm_prep)) {
  names(ecm_prep)[i] <- ecm_prep[[i]][["name"]]
  ecm_prep[[i]][["name"]] <- NULL
}

# there is un-competed data in the ecm_prep object.  Extract it.

ecm_prep_market <- lapply(ecm_prep, getElement, "markets")

# str(ecm_prep_market[[1]], max.level = 1)

# the length of the lists suggest breaking apart the markets data into two sets
str(ecm_prep_market[[1]][["Technical potential"]], max.level = 1)
str(ecm_prep_market[[1]][["Max adoption potential"]], max.level = 1)

ecm_prep_market_master_mseg <- lapply(ecm_prep_market, lapply, getElement, "master_mseg")
ecm_prep_market_mseg_out_break <- lapply(ecm_prep_market, lapply, getElement, "mseg_out_break")

# str(ecm_prep_market_master_mseg[[1]][["Technical potential"]], max.level = 1)
# str(ecm_prep_market_mseg_out_break[[1]][["Max adoption potential"]], max.level = 1)
#
# str(ecm_prep_market_mseg_out_break[[1]][["Max adoption potential"]][["energy"]]$savings[[1]][[4]][[1]], max.level = 1)
# str(ecm_prep_market_mseg_out_break[[1]][["Max adoption potential"]][["carbon"]]$savings, max.level = 1)
# str(ecm_prep_market_mseg_out_break[[1]][["Max adoption potential"]][["cost"]]$savings, max.level = 1)

x <- lapply(ecm_prep_market_mseg_out_break,
            lapply, lapply, lapply, lapply, lapply, lapply,
            data.table::as.data.table)

x <- lapply(x,
            lapply, lapply, lapply, lapply, lapply,
            data.table::rbindlist, idcol = "lvl7")

x <- lapply(x,
            lapply, lapply, lapply, lapply,
            data.table::rbindlist, idcol = "lvl6")

x <- lapply(x,
            lapply, lapply, lapply,
            data.table::rbindlist, idcol = "lvl5")

x <- lapply(x,
            lapply, lapply,
            data.table::rbindlist, idcol = "lvl4")

x <- lapply(x,
            lapply,
            data.table::rbindlist, idcol = "lvl3")

x <- lapply(x,
            data.table::rbindlist, idcol = "adoption_scenario")

x <- data.table::rbindlist(x, idcol = "ecm")

x <- data.table::melt(x,
                      id.vars = c("ecm", "adoption_scenario", "lvl3", "lvl4",
                                  "lvl5", "lvl6", "lvl7"),
                      variable.factor = FALSE,
                      variable.name = "year")

################################################################################
# storage modes
x[, year := as.integer(year)]


################################################################################
# save the wanted objects as .rds files
saveRDS(x, file = "./results/plots/uncompleted_markets.rds")

################################################################################
###                               End of File                                ###
################################################################################

