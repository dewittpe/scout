################################################################################
###                   Define User Interface for Shiny App                    ###
################################################################################


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
                                                                    uiOutput("ecm_select_ui"))
                                      ) # end of sidebarPanel
                                      ,
                                      mainPanel(
                                                tabsetPanel(
                                                            type = "tabs",
                                                            tabPanel("Notes", includeMarkdown("notes.md")),
                                                            tabPanel("Financial Metrics", plotly::plotlyOutput("fm_plot")),
                                                            tabPanel("CO\u2082 Emmissions", uiOutput("co2emmissions_ui")),
                                                            tabPanel("Cost Effective Avoided CO\u2082", "under construction"),
                                                            tabPanel("Total Avoided CO\u2082", "under construciton")
                                                ) # end tabsetPanel
                                      ) # end mainPanel
                                      ), # end of sidebarLayout
) # end of fluidPage
) # end shinyUI

################################################################################
###                               End of File                                ###
################################################################################
