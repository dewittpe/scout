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
                                                                label = "For Financial Metrics",
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
                                                                    selectInput(inputId = "ecm_checkbox",
                                                                                label = "Select ECMs",
                                                                                choices = sort(unique(ms$ecm)),
                                                                                multiple = TRUE,
                                                                                selectize = FALSE
                                                                                ))
                                      ) # end of sidebarPanel
                                      ,
                                      mainPanel(
                                                tabsetPanel(
                                                            type = "tabs",
                                                            tabPanel("Notes", includeMarkdown("notes.md")),
                                                            tabPanel("Financial Metrics", plotly::plotlyOutput("fm_plot")),
                                                            tabPanel("CO\u2082 Emmissions", uiOutput("co2emmissions_ui"))#plotOutput("co2emmissions"))
                                                ) # end tabsetPanel
                                      ) # end mainPanel
                                      ), # end of sidebarLayout
) # end of fluidPage
) # end shinyUI

################################################################################
###                               End of File                                ###
################################################################################
