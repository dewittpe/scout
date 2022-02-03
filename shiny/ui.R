################################################################################
###                   Define User Interface for Shiny App                    ###
################################################################################

library(shiny)
library(data.table)
library(ggplot2)
library(plotly)

ui <- shinyUI(fluidPage(
                        titlePanel("Scout ECM Summaries"),

                        sidebarLayout(
                                      sidebarPanel(
                                                   width = 3
                                                   ,
                                                   radioButtons(inputId = "ecm_agg",
                                                                label = "",
                                                                choices = c("Aggregate ECMs" = 1, "Speghitti Plot" = 2),
                                                                selected = 1)
                                                   ,
                                                   radioButtons(inputId = "all_ecms",
                                                                label = "Subset ECMs",
                                                                choices = c("All ECMs" = 1, "Select Specific ECM(s)" = 2),
                                                                selected = 1)
                                                   ,
                                                   conditionalPanel(
                                                                    condition = "input.all_ecms == '2'",
                                                                    checkboxGroupInput(inputId = "ecm_checkbox",
                                                                                       "Select ECMs",
                                                                                       sort(unique(ms$ecm))))
                                      ) # end of sidebarPanel
                                      ,
                                      mainPanel(
                                                tabsetPanel(
                                                            type = "tabs",
                                                            tabPanel("Financial Metrics", plotly::plotlyOutput("fm_plot")),
                                                            tabPanel("...placeholder...", plotOutput("mainplot"))
                                                ) # end tabsetPanel
                                      ) # end mainPanel
                                      ), # end of sidebarLayout
) # end of fluidPage
) # end shinyUI

################################################################################
###                               End of File                                ###
################################################################################
