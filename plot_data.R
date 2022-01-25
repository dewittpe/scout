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

# save the object as a .rds object
saveRDS(ecm_prep, file = "./results/plots/ecm_prep.rds")


################################################################################
###                               End of File                                ###
################################################################################

