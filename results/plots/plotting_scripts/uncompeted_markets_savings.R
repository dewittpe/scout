
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

# first level of the object are the ECMs, under that are the adoption scenarios
str(ecm_prep_market[[1]], max.level = 1)

# the length of the lists suggest breaking apart the markets data into two sets
str(ecm_prep_market[[1]][["Technical potential"]], max.level = 1)
str(ecm_prep_market[[1]][["Max adoption potential"]], max.level = 1)

ecm_prep_market_master_mseg <- lapply(ecm_prep_market, lapply, getElement, "master_mseg")
ecm_prep_market_mseg_out_break <- lapply(ecm_prep_market, lapply, getElement, "mseg_out_break")

# Explore the structure of the two lists.  For master_mseg there are common
# structures but at different levels... for example:
# ecm -- adoption_scenario -- energy/carbon -- total/competed -- baseline/efficient
# ecm -- adoption_scenario -- cost -- energy/carbon -- total/competed -- baseline/efficient
# 
# WHY ARE THERE COMPETED VALUES?
#
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]], max.level = 1)

str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]][["total"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]][["total"]][["all"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]][["total"]][["measure"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]][["competed"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]][["competed"]][["all"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["stock"]][["competed"]][["measure"]], max.level = 1)

str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]][["total"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]][["total"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]][["total"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]][["competed"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]][["competed"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["energy"]][["competed"]][["efficient"]], max.level = 1)

str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]][["total"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]][["total"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]][["total"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]][["competed"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]][["competed"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["carbon"]][["competed"]][["efficient"]], max.level = 1)

str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]][["total"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]][["total"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]][["total"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]][["competed"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]][["competed"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["stock"]][["competed"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]][["total"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]][["total"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]][["total"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]][["competed"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]][["competed"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["energy"]][["competed"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]][["total"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]][["total"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]][["total"]][["efficient"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]][["competed"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]][["competed"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["cost"]][["carbon"]][["competed"]][["efficient"]], max.level = 1)

str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["lifetime"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["lifetime"]][["baseline"]], max.level = 1)
str(ecm_prep_market_master_mseg[[1]][["Technical potential"]][["lifetime"]][["measure"]], max.level = 1)



str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]], max.level = 1)

str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ1"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ1"]][["Residential (New)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ1"]][["Residential (Existing)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ1"]][["Commercial (New)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ1"]][["Commercial (New)"]][["Heating (Equip.)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ1"]][["Commercial (Existing)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ2"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ3"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ4"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["baseline"]][["AIA CZ5"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ1"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ1"]][["Residential (New)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ1"]][["Residential (Existing)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ1"]][["Commercial (New)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ1"]][["Commercial (New)"]][["Heating (Equip.)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ1"]][["Commercial (Existing)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ2"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ3"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ4"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["efficient"]][["AIA CZ5"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ1"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ1"]][["Residential (New)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ1"]][["Residential (Existing)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ1"]][["Commercial (New)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ1"]][["Commercial (New)"]][["Heating (Equip.)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ1"]][["Commercial (Existing)"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ2"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ3"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ4"]], max.level = 1)
str(ecm_prep_market_mseg_out_break[[1]][["Technical potential"]][["energy"]][["savings"]][["AIA CZ5"]], max.level = 1)


x <- lapply(ecm_prep_market_mseg_out_break,
            lapply, lapply, lapply, lapply, lapply, lapply,
            data.table::as.data.table)

x <- lapply(x,
            lapply, lapply, lapply, lapply, lapply,
            data.table::rbindlist, idcol = "end_use")

x <- lapply(x,
            lapply, lapply, lapply, lapply,
            data.table::rbindlist, idcol = "building_class")

x <- lapply(x,
            lapply, lapply, lapply,
            data.table::rbindlist, idcol = "region")

x <- lapply(x,
            lapply, lapply,
            data.table::rbindlist, idcol = "results_scenario")

x <- lapply(x,
            lapply,
            data.table::rbindlist, idcol = "ecc")

x <- lapply(x,
            data.table::rbindlist, idcol = "adoption_scenario")

x <- data.table::rbindlist(x, idcol = "ecm")

x <- data.table::melt(x,
                      id.vars = c("ecm", "adoption_scenario", "ecc",
                                  "results_scenario",
                                  "region", "building_class", "end_use"),
                      variable.factor = FALSE,
                      variable.name = "year")


################################################################################
# storage modes
x[, year := as.integer(year)]

# competed/uncompleted status
x[, competed := 0L]

# Simplify end uses
x[, end_use2 := end_use]

x[
  end_use %in% c("Cooling (Equip.)", "Heating (Equip.)", "Ventilation"),
  end_use2 := "HVAC"]

x[
  end_use %in% c("Cooling (Env.)", "Heating (Env.)"),
  end_use2 := "Envelope"]

x[
  end_use %in% c("Computers and Electronics"),
  end_use2 := "Electronics"]

x[
  , end_use2 := factor(end_use2,
                       levels = c('HVAC', 'Envelope', 'Lighting',
                                  'Water Heating', 'Refrigeration',
                                  'Cooking', 'Electronics', 'Other'))]

################################################################################
# save the wanted objects as .rds files
saveRDS(x, file = "./results/plots/uncompeted_markets_savings.rds")

################################################################################
###                               End of File                                ###
################################################################################

