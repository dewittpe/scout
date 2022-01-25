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
################################################################################

################################################################################
###                       Check for needed R packages                        ###

# check for needed packages -- do not attached the namespaces.  Use the
# namespaces explicitly to alleviate possible issues from end users evaluating
# the script in an R environment where packages have been loaded in a different
# order, i.e., with a different search tree.

needed_pkgs <- c("data.table", "rjson", "pkg1", "pkg2")
needed_pkgs <- needed_pkgs[!(needed_pkgs %in% rownames(installed.packages()))]

if (length(needed_pkgs) > 0L) {
  x <- substitute(install.packages(pkgs, repo = "https://cran.rstudio.com"), list(pkgs = needed_pkgs))
  stop(paste("At least one needed package is not available.  Please install:\n",
             paste(needed_pkgs, collapse = ", "), "\n\ntry:\n"
             ))
}

x


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

################################################################################
###                               End of File                                ###
################################################################################

