# This script takes as input a data frame with columns that contain categorical values and computes the frequency of 
# each value for a given column, as well as the percentage of each value with respect to the total number of rows. 
# It also exports the results to an Excel file.

library(plyr)
library(xlsx)

# Read data
df = read.csv("cdereport-v2.csv", header = TRUE)

# Function that calculates the frequency (and %) of categorical values in a data frame column
calculate_frequencies <- function(df_column_name, export=TRUE) {
  freq_df <- count(df, df_column_name)
  percentage <- (freq_df$freq / nrow(df)) * 100
  percent_df <- cbind(freq_df, percentage)
  percent_df_sorted <- percent_df[order(percent_df$freq, decreasing=TRUE),]
  percent_df_sorted
  # export
  write.xlsx(percent_df_sorted, paste(df_column_name, "_frequencies.xlsx", sep=""))
  return(percent_df_sorted)
}

df_freq_datatype <- calculate_frequencies("datatype")
df_freq_units <- calculate_frequencies("units")

