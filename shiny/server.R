################################################################################
###                       Define Server for Shiny App                        ###
################################################################################

library(shiny)
library(data.table)
library(ggplot2)
library(plotly)

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

  ms_data  <- reactive({ ms })
  fm_data  <- reactive({ fm })

  output$ecm_select_ui <- renderUI({ #{{{
    selectInput(inputId = "ecm_checkbox",
                label = "Select ECMs",
                choices = sort(unique(ms_data()$ecm)),
                multiple = TRUE,
                selectize = FALSE
    )
  }) # }}}

  output$fm_plot <- plotly::renderPlotly({ #{{{

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

  }) # }}}

  co2emmissions_plot_height <- reactive(max(200, 200 * length(input$ecm_checkbox)))

  observe({output$co2emmissions_plot <- plotly::renderPlotly({ #{{{
    d <- ms_data()

    # d <- data.table::copy(ms) # for dev work
    d <- subset(d, ecc == "carbon")
    d <- subset(d, results_scenario %in% c("baseline", "efficient"))

    if (input$all_ecms == "1") {
      g <- ggplot2::qplot(x = 1, y = 1, geom = "text", label = "select between 1 and 12 ecms to plot") +
        ggplot2::theme_void()
      return(plotly::ggplotly(g))
    } else {
      d <- subset(d, ecm %in% input$ecm_checkbox)
      if (nrow(d) == 0) {
        g <- ggplot2::qplot(x = 1, y = 1, geom = "text", label = "select between 1 and 12 ecms to plot") +
          ggplot2::theme_void()
        return(plotly::ggplotly(g))
      } else if (length(unique(d$ecm)) > 12) {
        g <- ggplot2::qplot(x = 1, y = 1, geom = "text", label = "select 12 or fewer ecms") +
          ggplot2::theme_void()
        return(plotly::ggplotly(g))
      }
    }

    d <-
      d[, .(value = sum(value),
            region = paste(unique(region), collapse = ", "),
            building_class = paste(unique(building_class), collapse = ", "),
            end_uses = paste(unique(end_use), collapse = ", ")
            ),
        by = .(ecm, adoption_scenario, year, results_scenario, competed)]


    g <-
    # ggplot2::ggplot(d[grepl("Wall", ecm)]) + # for dev work
    ggplot2::ggplot(d) +
      ggplot2::theme_bw() +
      ggplot2::aes(x = year, y = value, color = results_scenario, linetype = competed) +
      ggplot2::geom_text(data = function(x) {
                           dd <- unique(x[, .(ecm, end_uses = paste("End Uses:", end_uses))])
                           dd[, year := mean(x$year)]
                           dd[, value := max(x$value) * 1.10]
                           dd
            },
                         mapping = ggplot2::aes(x = year, y = value, label = end_uses),
            inherit.aes = FALSE
            ) +
      ggplot2::geom_line() +
      ggplot2::scale_x_continuous(breaks = seq(2025, 2050, by = 5),
                                  minor_breaks = seq(2022, 2050, by = 1)) +
      ggplot2::facet_grid(ecm ~ adoption_scenario) +
      ggplot2::ylab("CO\u2082 Emmissions (MMTons)")

      return(plotly::ggplotly(g))

  }, # height = co2emmissions_plot_height()
  )
  })#}}}

  output$co2emmissions_ui <- renderUI({
    plotlyOutput("co2emmissions_plot", height = co2emmissions_plot_height())
  })

}


################################################################################
###                               End of File                                ###
################################################################################

