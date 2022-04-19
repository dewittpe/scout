################################################################################
# File: input_data_eda.R
#
# Purpose: exploratory data analysis of the input data for plotting.
#
# THIS SCRIPT IS NOT EXPECTED TO BE FULLY EXECUTABLE -- IT IS A SANDBOX
#
#
# Look to see if the same results (data) as the .xlsx files from the plots.R
# script are found in the data set construction by DeWitt.
#
################################################################################
rm(list = ls())

################################################################################
#                                 Data Import                                  #

###
### import data sets constructed by DeWitt
###
fm  <- data.table::setDT(readRDS("./results/plots/financial_metrics.rds"))
cms <- data.table::setDT(readRDS("./results/plots/competed_markets_savings.rds"))
ums <- data.table::setDT(readRDS("./results/plots/uncompeted_markets_savings.rds"))
ms <- rbind(cms, ums, fill = TRUE)
ms[, competed := factor(competed, 0:1, c("uncompeted", "competed"))]

# It appears that the IRR percent in fm needs a unit conversion with some
# conditions.  Treat 999 as "unknown"
fm[grepl("IRR", variable) & value != 999, value := value * 100]

###
### import data created by plots.R
###
#
xlsx <- list()
xlsx$map_total_energy <-
  readxl::read_xlsx(
    path = "./results/plots/max_adopt_potential/Summary_Data-MAP.xlsx",
    sheet = "Total Energy")
xlsx$map_total_co2 <-
  readxl::read_xlsx(
    path = "./results/plots/max_adopt_potential/Summary_Data-MAP.xlsx",
    sheet = "Total CO2")
xlsx$map_total_cost <-
  readxl::read_xlsx(
    path = "./results/plots/max_adopt_potential/Summary_Data-MAP.xlsx",
    sheet = "Total Cost")
xlsx$tp_total_energy <-
  readxl::read_xlsx(
    path = "./results/plots/tech_potential/Summary_Data-TP.xlsx",
    sheet = "Total Energy")
xlsx$tp_total_co2 <-
  readxl::read_xlsx(
    path = "./results/plots/tech_potential/Summary_Data-TP.xlsx",
    sheet = "Total CO2")
xlsx$tp_total_cost <-
  readxl::read_xlsx(
    path = "./results/plots/tech_potential/Summary_Data-TP.xlsx",
    sheet = "Total Cost")


# combine the elements of xlsx into one data.table so the format is similar to
# the format of the data set DeWitt constructed.
xlsx[[1]]$adoption_scenario <- "Max adoption potential"
xlsx[[2]]$adoption_scenario <- "Max adoption potential"
xlsx[[3]]$adoption_scenario <- "Max adoption potential"
xlsx[[4]]$adoption_scenario <- "Technical potential"
xlsx[[5]]$adoption_scenario <- "Technical potential"
xlsx[[6]]$adoption_scenario <- "Technical potential"

for(i in seq_along(xlsx)) {
  data.table::setDT(xlsx[[i]])
  xlsx[[i]] <-
    data.table::melt(xlsx[[i]], measure.vars = grep("^\\d+", names(xlsx[[i]])))
}

xlsx <- data.table::rbindlist(xlsx, use.names = TRUE, fill = TRUE)


# get consistent names and data structures between the ms and xlsx data sets
data.table::setnames(xlsx, old = "ECM Name", new = "ecm")
data.table::setnames(xlsx, old = "Climate Zones", new = "region")
data.table::setnames(xlsx, old = "Building Classes", new = "building_classes")
data.table::setnames(xlsx, old = "End Uses", new = "end_uses")
data.table::setnames(xlsx, old = "Results Scenario", new = "results_scenario")

xlsx[, year := as.integer(sub("^(\\d{4}).+", "\\1", variable))]
# xlsx[, variable := sub("^(\\d{4})\\s\\((.+)\\)$", "\\2", variable)]
xlsx[grepl("Quads", variable), ecc := "energy"]
xlsx[grepl("Mt", variable), ecc := "carbon"]
xlsx[grepl("\\$", variable), ecc := "cost"]

xlsx[results_scenario %in% c("Baseline competed", "Efficient competed"), competed := 1L]
xlsx[results_scenario %in% c("Baseline uncompeted", "Efficient uncompeted"), competed := 0L]

xlsx[results_scenario %in% c("Baseline competed", "Baseline uncompeted"), results_scenario := "baseline"]
xlsx[results_scenario %in% c("Efficient competed", "Efficient uncompeted"), results_scenario := "efficient"]

xlsx[, competed := factor(competed, 0:1, c("uncompeted", "competed"))]

################################################################################
#                              Financial Metrics                               #

# the xlxs data has the financial metrics for 2050

xlsx_fm <-
  subset(xlsx,
         select = c(
                    "ecm",
                    "IRR (%), 2050", "Payback (years), 2050",
                    "CCE ($/MMBtu saved), 2050", "CCC ($/tCO2 avoided), 2050"
                    )
  )

# check the assumption that the number of unique rows for the 2050 financial
# metrics is equal to the number of unique ecms.
stopifnot(nrow(unique(xlsx_fm)) == length(unique(xlsx$ecm)))

# melt the xlsx_fm to make it easy to compare with fm values
xlsx_fm <-
  data.table::melt(xlsx_fm,
                   id.vars = "ecm",
                   variable.factor = FALSE,
                   variable.name = "xlsx_name",
                   value.name = "xlsx_value")

fm_2050 <- fm[year == 2050, .(ecm, fm_name = variable, fm_value = value)]

fm_2050[grepl("IRR", fm_name), metric := "IRR"]
fm_2050[grepl("Payback", fm_name), metric := "Payback"]
fm_2050[grepl("Conserved Energy", fm_name), metric := "CCE"]
fm_2050[grepl("Conserved CO", fm_name), metric := "CCC"]

xlsx_fm[grepl("IRR", xlsx_name), metric := "IRR"]
xlsx_fm[grepl("Payback", xlsx_name), metric := "Payback"]
xlsx_fm[grepl("CCE", xlsx_name), metric := "CCE"]
xlsx_fm[grepl("CCC", xlsx_name), metric := "CCC"]

fm_test <- merge(fm_2050, xlsx_fm, all = TRUE, by = c('ecm', 'metric'))
fm_test <- subset(fm_test, !is.na(xlsx_value))

# set a test with a tolerance for machine percision
fm_test[, fm_equal_xlsx := (fm_value > xlsx_value - (.Machine$double.eps)^(0.5)) &
                           (fm_value < xlsx_value + (.Machine$double.eps)^(0.5))]

# are there values that differ between the two data sets? -- YES
stopifnot(nrow(fm_test[!(fm_equal_xlsx)]) > 0L)

# the differences are machine percision differences:
fm_test2 <-
  fm_test[!(fm_equal_xlsx), .(ecm, fm_value, xlsx_value, delta = abs(fm_value - xlsx_value))]

stopifnot(max(fm_test2$delta) < 1e-05)

################################################################################
#                                Compare Costs                                 #

xlsx_cost <-
  subset(xlsx,
         subset = ecc == "cost" & ecm != "All ECMs",
         select = c("ecm", "year", "results_scenario", "region",
                    "building_classes", "end_uses", "adoption_scenario",
                    "competed", "value")
         )

ms_cost <-
  subset(ms,
         subset = ecc == "cost" & results_scenario != "savings",
         select = c('ecm', 'year', 'region', 'building_class', 'end_use',
                    "results_scenario", 'adoption_scenario', 'value', "competed")
         )

ms_cost <-
  ms_cost[,
          .(
            .N
            , value = sum(value)
            , building_classes = paste(unique(building_class), collapse = ', ')
            , region = paste(unique(region), collapse = ', ')
            , end_uses = paste(unique(end_use), collapse = ', ')
            ),
          by = .(ecm, year, adoption_scenario, results_scenario, competed)
         ]


xlsx_cost[ecm == "Prospective Commercial SSL"]
ms_cost[ecm == "Prospective Commercial SSL"]

test_cost <-
  merge(ms_cost, xlsx_cost, all = TRUE,
        by = c("ecm", "year", "adoption_scenario", "results_scenario", "competed"
               #, "building_classes", "region"
               #, "end_uses"
               ),
        suffixes = c("_ms", "_xlsx"))

test_cost

# unit change needed.  it looks like DeWitt's set is in dollars and the xlsx
# data is in billions
test_cost[, value_ms := value_ms * 1e-9]

test_cost[, percent_delta := 100 * abs(value_ms - value_xlsx) / value_xlsx]

# ggplot2::ggplot(test_cost[percent_delta > 1e-8]) +
ggplot2::ggplot(test_cost[percent_delta > 1]) +
  ggplot2::theme_bw() +
  ggplot2::aes(x = value_ms, y = value_xlsx, color = ecm) +#factor(year)) +#, color = building_classes_ms, shape = building_classes_xlsx) +
  ggplot2::geom_point(alpha = 0.8) +
  ggplot2::geom_abline(intercept = 0, slope = 1) +
  ggplot2::facet_wrap(~ adoption_scenario + results_scenario + building_classes_ms, scales = "free") +
  ggplot2::ggtitle("observations were 100 * abs(value_ms - value_xlsx) / value_xlsx > 1")

# differences are only on competed values?
stopifnot(test_cost[percent_delta > 1e-8, all(competed == "competed")])

test_cost[competed == "competed", .N]
test_cost[percent_delta > 1e-8, .N]

nrow(test_cost)
nrow(test_cost[percent_delta > 1e-8])
nrow(test_cost[percent_delta > 0.01])

# Why are there rows in test_cost that do not have both _ms and _xlsx values?
test_cost[building_classes_ms != building_classes_xlsx]
test_cost[end_uses_ms != end_uses_xlsx]

# one possible issue -- the building classes
# xlsx have only two options whereas ms has six
stopifnot(length(unique(xlsx_cost$building_classes)) == 2L)
stopifnot(length(unique(ms_cost$building_classes)) == 6L)
xlsx_cost[, unique(building_classes)]
ms_cost[, unique(building_classes)]

# if we ignore the building classes a visual spot check suggests there are still
# differences between the sets with respect to the cost saving values.

################################################################################
#                                    Carbon                                    #
xlsx_carbon <-
  subset(xlsx,
         subset = ecc == "carbon" & ecm != "All ECMs",
         select = c("ecm", "year", "results_scenario", "region",
                    "building_classes", "end_uses", "adoption_scenario",
                    "competed", "value")
         )

ms_carbon <-
  subset(ms,
         subset = ecc == "carbon" & results_scenario != "savings",
         select = c('ecm', 'year', 'region', 'building_class', 'end_use',
                    "results_scenario", 'adoption_scenario', 'value', "competed")
         )

ms_carbon <-
  ms_carbon[,
          .(
            .N
            , value = sum(value)
            , building_classes = paste(unique(building_class), collapse = ', ')
            , region = paste(unique(region), collapse = ', ')
            , end_uses = paste(unique(end_use), collapse = ', ')
            ),
          by = .(ecm, year, adoption_scenario, results_scenario, competed)
         ]


xlsx_carbon[ecm == "Prospective Commercial SSL"]
ms_carbon[ecm == "Prospective Commercial SSL"]

test_carbon <-
  merge(ms_carbon, xlsx_carbon, all = TRUE,
        by = c("ecm", "year", "adoption_scenario", "results_scenario", "competed",
               "building_classes", "region", "end_uses"),
        suffixes = c("_ms", "_xlsx"))

test_carbon[, percent_delta := 100 * abs(value_ms - value_xlsx) / value_xlsx]

ggplot2::ggplot(test_carbon[percent_delta > 1e-8]) +
  ggplot2::aes(x = value_ms, y = value_xlsx, color = end_uses) +
  ggplot2::geom_point() +
  ggplot2::geom_abline(intercept = 0, slope = 1) +
  ggplot2::facet_wrap( ~ adoption_scenario + results_scenario + competed)

# differences are only on competed values?
stopifnot(test_carbon[percent_delta > 1e-8, all(competed == "competed")])

test_carbon[percent_delta > 1e-8]

# Why are there rows in test_carbon that do not have both _ms and _xlsx values?
test_carbon[is.na(value_ms) | is.na(value_xlsx)]

# one possible issue -- the building classes
# xlsx have only two options whereas ms has six
stopifnot(length(unique(xlsx_carbon$building_classes)) == 2L)
stopifnot(length(unique(ms_carbon$building_classes)) == 6L)
xlsx_carbon[, unique(building_classes)]
ms_carbon[, unique(building_classes)]

test_carbon <-
  merge(ms_carbon, xlsx_carbon, all = TRUE,
        by = c("ecm", "year", "adoption_scenario", "results_scenario", "competed"
               #, "building_classes"
               , "region"
               # , "end_uses"
               ),
        suffixes = c("_ms", "_xlsx"))
test_carbon[is.na(value_ms) | is.na(value_xlsx)]
test_carbon

if (nrow(
test_carbon[!(value_ms > value_xlsx - .Machine$double.eps^0.5 & value_ms < value_xlsx + .Machine$double.eps^0.5) ]
) == 0L) {
  message("carbon seems to be okay between ms an xlsx")
} else {
  message("carbon may differ between ms and xlsx")
}


################################################################################
###                               End of File                                ###
################################################################################

