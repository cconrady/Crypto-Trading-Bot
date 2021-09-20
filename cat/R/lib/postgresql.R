# SQL - PostgreSQL
if(!require(DBI)) {install.packages("RPostgres"); library(DBI)}

# [i] PostgreSQL
get_slq_data <- function(query) {
  
  # connect to postgres database
  
  con <- dbConnect(RPostgres::Postgres(), # <------ ENTER YOUR OWN SECURE DETAILS HERE
                   dbname = 'catdb', 
                   host = 'localhost',
                   port = 5432,
                   user = 'postgres',
                   password = 'password')
  
  # send Query
  res <- dbSendQuery(con, query)
  # return data
  df <- data.frame(dbFetch(res))
  # clear result and dc from db
  dbClearResult(res)
  dbDisconnect(con)
  
  # return sql data as data frame
  return(df)
}