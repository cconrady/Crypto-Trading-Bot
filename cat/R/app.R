
#________________________________________________________________________________#
# NOTE:

VERSION = "v1.0.00"

# v1.0.00:
# - Reactive on both orders and status

## By default, Shiny is styled off Bootstrap 3.3
## https://getbootstrap.com/docs/3.3/
## A few modifications were made on top of this, saved in 'www/bootstrap_mod.css'

#________________________________________________________________________________#
# [0] Clear memory

## remove variables
rm(list=ls())

## remove variables and packages
rm(list = ls(all.names = TRUE))

## clear memory
gc()

#________________________________________________________________________________#
# [1] Load CRAN libraries

## shiny
if(!require(shiny)) {install.packages("shiny"); library(shiny)}

## data frame manipulation
if(!require(tidyverse)) {install.packages("tidyverse"); library(tidyverse)}
if(!require(lubridate)) {install.packages("lubridate"); library(lubridate)}

## data tables
if(!require(data.table)) {install.packages("data.table"); library(data.table)}
if(!require(formattable)) {install.packages("formattable"); library(formattable)}
#if(!require(DT)) {install.packages("DT"); library(DT)}

# SQL - PostgreSQL
if(!require(DBI)) {install.packages("RPostgres"); library(DBI)}

# Other
if(!require(base64enc)) {install.packages("base64enc"); library(base64enc)}

## plots
# if(!require(ggplot2)) {install.packages("ggplot2"); library(ggplot2)}
# if(!require(plotly)) {install.packages("plotly"); library(plotly)}

#________________________________________________________________________________#
# [2] Include from \lib (custom functions)

if(!exists("foo", mode="function")) source("lib/custom_tables.R")
if(!exists("foo", mode="function")) source("lib/postgresql.R")

#________________________________________________________________________________#
# [3] Prepare data for ui & server

# main tables
df_orders <- get_slq_data("SELECT * FROM app_orders;")
df_status <- get_slq_data("SELECT * FROM app_status;")

# other (arguments for inputs, etc.)
i1_choices <- c("lun", "val")
i1_selected <- i1_choices
names(i1_choices) <- c("Luno", "Valr")

#______________________________________________________________________________________________________________#
# ui ----------------------------------------------------------------------------------------------------------0

#________________________________________________________________________________#
# (NOTE: This line tries to separate sections to make it easier to read.)
# 0: ui/ server
# 1: Ascending indent levels
# S: Keyword search

ui <- navbarPage( #S: navbarpage0
  title = "SA Crypto Arbitrage"
  ,id = "navbar"
  ,theme = "css/mod.css" # small modifications to some elements
  
  #________________________________________________________________________________#      
  # 'Home' tab ------------------------------------------------------------------------------------------------1
  ,tabPanel("Home", icon = icon("home") #S: Home1
      
      ,fluidRow( #S: FluidRow1.2
      # filter, quick selection, data table
          column(10, offset=1 #S: Column1.2.1
                 
              # ----------------------------------------------------------------------------------------------99
              # API Status Table
              ,tags$h5(tags$strong("API Status"))
              ,actionButton(inputId = "refresh", label = "", icon = icon("sync"))
              ,formattableOutput(outputId="o2")
              ,tags$hr()
                 
              # ----------------------------------------------------------------------------------------------99
              # Filter input for 'market' & 'coin'
              ,selectInput(
                  inputId = "i1"
                  ,label = "Filter"
                  ,choices = i1_choices
                  ,selected = i1_selected
                  ,multiple = TRUE
              ) # selectInput
              
              # ----------------------------------------------------------------------------------------------99
              # Quick selection for 'market' & 'coin'
              ,tags$h5(tags$strong("Quick Selection Tool"))
              ,wellPanel(
                   actionButton(inputId = "selectDefault",  label = "Default",        icon = icon("redo"))
                  ,actionButton(inputId = "selectLun",      label = "Luno")
                  ,actionButton(inputId = "selectVal",      label = "Valr")
              ) # wellPanel
              
              # ----------------------------------------------------------------------------------------------99
              # Orders Table
              ,formattableOutput(outputId="o1")
              ,tags$hr()

          ) # column: Column1.2.1
          
      ) # fluidRow: FluidRow1.2
    
  ) # tabPanel: Home1
           
  #________________________________________________________________________________#
  # 'How to use' Tab ------------------------------------------------------------------------------------------1
  ,tabPanel("How to use", icon = icon("info") #S: HowToUse2
      # (whitespace)
      ,tags$div(style="height: 100px;")
  ) # tabPanel: HowToUse2
  
) # navbarpage0


#________________________________________________________________________________#
# server ------------------------------------------------------------------------------------------------------0

server <- function(input, output, session) { #S: server0
  
  # Update Data (reactively) ---------------------------------------------------A
  orders <- reactive({
    if (input$refresh >= 0) {
      df_orders <- get_slq_data("SELECT * FROM app_orders;")
    }
    df_orders %>% filter(market %in% input$i1)
  })
  
  status <- reactive({
    if (input$refresh >= 0) {
      df_status <- get_slq_data("SELECT * FROM app_status;")
    }
  })
  
  # Observe Events -------------------------------------------------------------B
  observeEvent(input$selectDefault, {
    updateSelectInput(session, inputId="i1", selected = i1_selected
    ) # updateSelectInput
  }) # observeEvent: selectDefault
  
  observeEvent(input$selectLun, {
    updateSelectInput(session, inputId="i1", selected = unique(c(input$i1, "lun"))
    ) # updateSelectInput
  }) # observeEvent: selectLun
  
  observeEvent(input$selectVal, {
    updateSelectInput(session, inputId="i1", selected = unique(c(input$i1, "val"))
    ) # updateSelectInput
  }) # observeEvent: selectVal
  
  # Render Outputs -------------------------------------------------------------C

  output$o1 <- renderFormattable({
    df <- data.frame(orders()) %>% 
      arrange(desc(margin)) %>%
      mutate(
        coin_desc = coin,
        market_desc = market) %>%
      select(coin, coin_desc, market, market_desc, price, volume, total, margin) %>%
        mutate(
          price = currency(price, symbol = "R", digits = 2L, format = "f", big.mark = ",", sep = ""),
          total = currency(total, symbol = "R", digits = 2L, format = "f", big.mark = ",", sep = ""),
          margin = percent(margin/100)
        ) %>%
        head(25) %>%
      formattable(
        align = c("r","l","r","l","r", "r", "r", "r"),
                list(
                  coin = formatter_images,
                  market = formatter_images,
                  total = formatter_bars_curr,
                  margin = formatter_arrows
                )
    )
    
  })
  
  output$o2 <- renderFormattable({
    df <- data.frame(status()) %>% 
      arrange(online) %>% 
      mutate(
        updated = Sys.time() - client_timestamp
        ,ticker1_desc = ticker1
      ) %>%
      select(name, ticker1, ticker1_desc, everything()) %>%
      arrange(name, ticker1) %>%
      formattable(
                align = c("l","r","l", "c", "c", "c", "c", "c", "c", "c", "c"),
                list(
                  online = formatter_ticks
                  ,ticker1 = formatter_images
                  ,status_code = formatter_bars_code
                )
    )
    
    
  })
  
} # server0

shinyApp(ui = ui, server = server)