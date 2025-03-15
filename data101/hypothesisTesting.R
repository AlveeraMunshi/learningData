install.packages("nycflights13")
library("nycflights13")
devtools::install_github("janish-parikh/ZTest")
library(HypothesisTesting)

data(flights)

p<- permutation_test(flights, "carrier", "air_time", 100, "UA", "DL")

# Print the results
print(p)