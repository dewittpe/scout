################################################################################
###                       Define Server for Shiny App                        ###
################################################################################

# data import
fm  <- data.table::setDT(readRDS("../results/plots/financial_metrics.rds"))
cms <- data.table::setDT(readRDS("../results/plots/competed_markets_savings.rds"))
ums <- data.table::setDT(readRDS("../results/plots/uncompeted_markets_savings.rds"))
ms <- rbind(cms, ums, fill = TRUE)
ms[, competed := factor(competed, 0:1, c("uncompeted", "competed"))]

# It appears that the IRR percent in fm needs a unit conversion with some
# conditions.  Treat 999 as "unknown"
fm[grepl("IRR", variable) & value != 999, value := value * 100]

# server definition
server <- function(input, output, session) {

  ecm_data <- reactive({ ms })
  fm_data <- reactive({ fm })

  output$fm_plot <- plotly::renderPlotly({

    if (input$all_ecms == "1") {
      fm_plot_data <- fm_data()
    } else {
      fm_plot_data <- fm_data()[ecm %in% input$ecm_checkbox]
    }
    n_ecms <- length(unique(fm_plot_data$ecm))

    if (input$ecm_agg == "1") {
      fm_plot_data <- fm_plot_data[, .(ecm = "All ECMs", value = mean(value)), by = .(variable, year)]
      plot_title <- paste0("Average Values over all ", n_ecms, " ECMs")
    } else {
      plot_title <- paste0("Financial Metric Values for each of ", n_ecms, " ECMs")
    }

    # g <-
    #   ggplot2::ggplot(fm_plot_data) +
    #   ggplot2::aes(x = year, y = value, group = ecm) +
    #   ggplot2::geom_point() +
    #   ggplot2::geom_line() +
    #   ggplot2::facet_wrap( ~ variable, scales = "free_y") +
    #   ggplot2::ggtitle(label = plot_title) +
    #   ggplot2::ylab("") +
    #   ggplot2::theme(legend.title = ggplot2::element_blank(),
    #                  legend.position = "bottom")
    # if (n_ecms > 1 & n_ecms < 12) {
    #   g <- g + ggplot2::aes(color = ecm)
    # }
    # g


    d <- split(fm_plot_data, fm_plot_data$variable)
    clrs <- c("red", "blue", "green", "purple")

    ps <- list()
    for(i in seq_along(d)) {
      ps[[i]] <-
        plot_ly(group_by(d[[i]], ecm),
                x = ~ year,
                y = ~ value,
                text = ~ ecm,
                color = ~ variable,
                type = "scatter",
                mode = "lines+markers",
                hovertemplate = paste('ECM: %{text}<br>',
                                      'Year: %{x}<br>',
                                      'Value: %{y}<br>'),
                marker = list(color = clrs[i]),
                line = list(color = clrs[i])
                ) %>%
       layout(yaxis = list(exponentformat = "e"))
    }
    subplot(ps, nrows = 2, shareY = FALSE, shareX = TRUE, margin = 0.05)

  })


  output$mainplot <- renderPlot({
    ggplot2::ggplot(mtcars) +
      ggplot2::aes(x = hp, y = mpg) +
      ggplot2::geom_point()
    # ggplot2::ggplot(ms[year == 2022]) +
    #   ggplot2::aes(x = year, y = value) +
    #   ggplot2::geom_point() +
    #   ggplot2::facet_grid(ecc ~ adoption_scenario + competed)
  })
}


################################################################################
###                               End of File                                ###
################################################################################

