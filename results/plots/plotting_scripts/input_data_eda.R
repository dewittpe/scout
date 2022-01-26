################################################################################
# File: input_data_eda.R
#
# Purpose: exploratory data analysis of the input data for plotting.
#
# THIS SCRIPT IS NOT EXPECTED TO BE FULLY EXECUTABLE -- IT IS A SANDBOX
#
#
#
################################################################################

################################################################################
###                       Check for needed R packages                        ###

# check for needed packages -- do not attached the namespaces.  Use the
# namespaces explicitly to alleviate possible issues from end users evaluating
# the script in an R environment where packages have been loaded in a different
# order, i.e., with a different search tree.

needed_pkgs <- c("data.table", "rjson")
needed_pkgs <- needed_pkgs[!(needed_pkgs %in% rownames(installed.packages()))]

if (length(needed_pkgs) > 0L) {
  x <- substitute(install.packages(pkgs, repo = "https://cran.rstudio.com"),
                  list(pkgs = needed_pkgs))
  stop(paste("At least one needed package is not available.  Please install:\n",
             paste(needed_pkgs, collapse = ", "),
             "\n\ntry the following to install the needed packages:\n",
             capture.output(print(x))
             ))
}
rm(needed_pkgs)

################################################################################
###                               JSON Imports                               ###
################################################################################

# Import uncompleted ECM energy, carbon, and cost data
ecm_prep <-
  rjson::fromJSON(file = file.path('.', 'supporting_data','ecm_prep.json'))

# Import competed ECM energy, carbon, and cost data
ecm_results <-
  rjson::fromJSON(file = file.path('.', 'results','ecm_results.json'))

# Import competed energy, carbon, and cost data summed across all ECMs
agg_results <-
  rjson::fromJSON(file = file.path('.', 'results','agg_results.json'))

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

x <- data.table::melt(x, measure.vars = as.character(2022:2050),
                      variable.factor = FALSE,
                      variable.name = "year")


to_data_table(depth =31)



# DO THIS AT THE END
# x <- lapply(x,
#             lapply, lapply, lapply, lapply, lapply, lapply,
#             function(x) {
#               data.table::melt(x, measure.vars = names(x),
#                             variable.factor = FALSE, variable.name = "year")
#             })

head(x)


################################################################################
###                           Part out ECM Results                           ###

# There is (are) non ecm related results in the ecm_results object, move them to
# a standalone object.
non_ecm_results <- ecm_results[setdiff(names(ecm_results), names(ecm_prep))]
ecm_results[setdiff(names(ecm_results), names(ecm_prep))] <- NULL
stopifnot(setequal(names(ecm_results), names(ecm_prep)))

filter_variables <-
  lapply(ecm_results, getElement, "Filter Variables")
markets_savings_overall <-
  lapply(ecm_results, getElement, "Markets and Savings (Overall)")
markets_savings_by_category <-
  lapply(ecm_results, getElement, "Markets and Savings (by Category)")
financial_metrics <-
  lapply(ecm_results, getElement, "Financial Metrics")

################################################################################
###                         Clean "Filter Variables"                         ###

# str(filter_variables, max.level = 1)
# str(filter_variables[[1]], max.level = 1)

################################################################################
###                   Clean Markets and Savings (Overall)                    ###

# append the ecm_results with the "All ECMs" results
markets_savings_overall[["All ECMs"]] <-
  agg_results[["All ECMs"]][["Markets and Savings (Overall)"]]

# coerce the year/value data into a data.table, this will be in a "wide" format
markets_savings_overall <-
  lapply(markets_savings_overall, lapply, lapply, data.table::as.data.table)

# pivot the data.tables to a "long format"
markets_savings_overall <-
  lapply(markets_savings_overall, lapply, lapply,
         function(x) {
           data.table::melt(x, measure.vars = names(x),
                            variable.factor = FALSE, variable.name = "year")
         })

# bind all the results into one data.table, level by level
markets_savings_overall <-
  lapply(markets_savings_overall, lapply,
         data.table::rbindlist, idcol = "variable")
markets_savings_overall <-
  lapply(markets_savings_overall,
         data.table::rbindlist, idcol = "adoption_scenario")
markets_savings_overall <-
  data.table::rbindlist(markets_savings_overall, idcol = "ecm")

# Check that the "All ECMs" rows are redundant
markets_savings_overall[, s := sum(value), by = .(adoption_scenario, variable, year)]
stopifnot(markets_savings_overall[ecm == "All ECMs", all.equal(value, s/2)])
markets_savings_overall[, s := NULL]

################################################################################
###                 Clean Markets and Savings (By Category)                  ###

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         lapply, lapply, lapply, lapply, lapply,
         data.table::as.data.table)

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         lapply, lapply, lapply, lapply, lapply,
         function(x) {
           data.table::melt(x,
                            measure.vars = names(x),
                            variable.factor = FALSE,
                            variable.name = "year")
         })

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         lapply, lapply, lapply, lapply,
         data.table::rbindlist, idcol = "end_use")

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         lapply, lapply, lapply,
         data.table::rbindlist,
         idcol = "building_class")

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         lapply, lapply,
         data.table::rbindlist,
         idcol = "region")

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         lapply,
         data.table::rbindlist,
         idcol = "variable")

markets_savings_by_category <-
  lapply(markets_savings_by_category,
         data.table::rbindlist,
         idcol = "adoption_scenario")

markets_savings_by_category <-
  data.table::rbindlist(markets_savings_by_category, idcol = "ecm")

################################################################################
###                         Clean Finaancial Metrics                         ###

financial_metrics <-
  lapply(financial_metrics, lapply, data.table::as.data.table)

financial_metrics <-
  lapply(financial_metrics, lapply,
         function(x) {
           data.table::melt(x,
                            measure.vars = names(x),
                            variable.factor = FALSE,
                            variable.name = "year")
         })

financial_metrics <-
  lapply(financial_metrics,
         data.table::rbindlist,
         idcol = "variable")

financial_metrics <-
  data.table::rbindlist(financial_metrics, idcol = "ecm")

################################################################################
###                         Clean On Site Generation                         ###
on_site_generation <- non_ecm_results[["On-site Generation"]]

on_site_generation <- lapply(on_site_generation, getElement, "By Category")

on_site_generation <-
  lapply(on_site_generation, lapply, lapply, data.table::as.data.table)

on_site_generation <-
  lapply(on_site_generation, lapply, lapply,
         function(x) {
           data.table::melt(x,
                            measure.vars = names(x),
                            variable.factor = FALSE,
                            variable.name = "year")
         })

on_site_generation <-
  lapply(on_site_generation, lapply,
         data.table::rbindlist, idcol = "building_type")

on_site_generation <-
  lapply(on_site_generation,
         data.table::rbindlist, idcol = "region")

on_site_generation <-
  data.table::rbindlist(on_site_generation, idcol = "variable")

################################################################################
###                   Checks and simplication of data sets                   ###

# check markets_savings_by_category vs markets_savings_overall -- verify that
# the values in the _overall version are just the sums of the values in the
# _by_category version.  If the test passes then ther is no need to carry
# forward the _overall version.
mso <-
  markets_savings_by_category[, value := sum(value),
                              by = .(ecm, adoption_scenario, variable, year)]

tst <-
  merge(markets_savings_overall, mso,
        by = c("ecm", "adoption_scenario", "variable", "year"))
stopifnot(all.equal(tst$value.x, tst$value.y))

markets_savings <- markets_savings_by_category
rm(markets_savings_by_category, markets_savings_overall, mso, tst)

# are any of the variables in the financial_metrics in the
# markets_savings_by_category?  --- NOTE: originally thought about binding
# financial_metrics with markets_savings, but that doesn't seem like a good idea
# after looking at the resulting data set.  Leaving this note here as a reminder
# of that.
stopifnot(!any(
               sapply(unique(financial_metrics$variable),
                      function(pattern) {
                        any(grepl(pattern, markets_savings$variable))
                      })
               ))

# do we need the filter_variables object?
# check for end uses
fveu <- lapply(filter_variables, getElement, "Applicable End Uses")
fveu <- lapply(fveu, data.table::as.data.table)
fveu <- data.table::rbindlist(fveu, idcol = "ecm")
data.table::setnames(fveu, "V1", "end_use")

# The following are the end uses listed in the filter_variables which are _not_
# in the markets_savings data.table
fveu[! unique(markets_savings[, .(ecm, end_use)]), on = c("ecm", "end_use")]

# any in markets_savings not in filter variables?
tst <-
  unique(markets_savings[, .(ecm, end_use)])[! fveu, on = c("ecm", "end_use")]
stopifnot(nrow(tst) == 0L)

# check for building classes
fvbc <- lapply(filter_variables, getElement, "Applicable Building Classes")
fvbc <- lapply(fvbc, data.table::as.data.table)
fvbc <- data.table::rbindlist(fvbc, idcol = "ecm")
data.table::setnames(fvbc, "V1", "building_class")

tst <-
  fvbc[!unique(markets_savings[, .(ecm, building_class)]),
       on = c("ecm", "building_class")]
stopifnot(nrow(tst) == 0L)

test <-
  unique(markets_savings[, .(ecm, building_class)]
         ) [! fvbc, on = c("ecm", "building_class")]
stopifnot(nrow(tst) == 0L)

# check for regions:
fvr <- lapply(filter_variables, getElement, "Applicable Regions")
fvr <- lapply(fvr, data.table::as.data.table)
fvr <- data.table::rbindlist(fvr, idcol = "ecm")
data.table::setnames(fvr, "V1", "region")

tst <- fvr[!unique(markets_savings[, .(ecm, region)]), on = c("ecm", "region")]
stopifnot(nrow(tst) == 0L)
tst <- unique(markets_savings[, .(ecm, region)])[!fvr, on = c("ecm", "region")]
stopifnot(nrow(tst) == 0L)

# NOTE: filter_variables are redundant with data in markets_savings

################################################################################
###                              Wanted Objects                              ###

# set storage modes
markets_savings[, year := as.integer(year)]
on_site_generation[, year := as.integer(year)]
financial_metrics[, year := as.integer(year)]

# build_class - split into building class (Commercial or Residential) and
# construction (New or Existing)
markets_savings[, construction := NA_character_]
markets_savings[grepl("New", building_class), construction := "New"]
markets_savings[grepl("Existing", building_class), construction := "Existing"]
markets_savings[, building_class := sub("^(.+)\\ \\(.+\\)$", "\\1", building_class)]

# Simplify end uses
markets_savings[, end_use2 := end_use]
markets_savings[end_use %in% c("Cooling (Equip.)", "Heating (Equip.)", "Ventilation"),
                end_use2 := "HVAC"]
markets_savings[end_use %in% c("Cooling (Env.)", "Heating (Env.)"),
                end_use2 := "Envelope"]
markets_savings[end_use %in% c("Computers and Electronics"),
                end_use2 := "Electronics"]

markets_savings[, end_use2 := factor(end_use2,
                                    levels = c('HVAC', 'Envelope', 'Lighting',
                                               'Water Heating', 'Refrigeration',
                                               'Cooking', 'Electronics',
                                               'Other'))]

# save the wanted objects as .rds files
saveRDS(ecm_prep,           file = "./results/plots/ecm_prep.rds")
saveRDS(markets_savings,    file = "./results/plots/markets_savings.rds")
saveRDS(on_site_generation, file = "./results/plots/on_site_generation.rds")
saveRDS(financial_metrics,  file = "./results/plots/financial_metrics.rds")

################################################################################
###                               End of File                                ###
################################################################################

