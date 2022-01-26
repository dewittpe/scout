################################################################################
# File: plot_data.R
#
# Purpose: construct data sets, combinations of lists and data.frames, which
# will be used for generating plots.  Functions for plotting are in separate
# scripts.
#
# This file is expected to be evaluated from the project root after
# `ecm_prep.py` and `run.py` have been evaluated.
#
# Generated data sets:
#
# | File                         | Description                                 |
# |:---------------------------- |:--------------------------------------------|
# | ./results/plots/ecm_prep.rds | A list structure of the ecm_prep json       |
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

################################################################################
###                               JSOM Imports                               ###
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

# Read in global metadata file
glob_run_vars <- rjson::fromJSON(file = file.path('.', 'glob_run_vars.json'))

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
  lapply(ecm_results, getElement, "Markets and Savings (By Category)")
financial_metrics <-
  lapply(ecm_results, getElement, "Financial Metrics")

################################################################################
###                         Clean "Filter Variables"                         ###

str(filter_variables, max.level = 1)
str(filter_variables[[1]], max.level = 1)

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

################################################################################
# save the object as a .rds object
saveRDS(ecm_prep, file = "./results/plots/ecm_prep.rds")

################################################################################
###                               End of File                                ###
################################################################################

