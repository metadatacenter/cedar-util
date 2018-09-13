# Analysis of ARM results

library(ggplot2)
library(gridExtra)
library(ggpubr)
#library(wesanderson)
library("RColorBrewer")


### CONSTANTS ###
workspace = "/Users/marcosmr/tmp/ARM_resources/EVALUATION/results"
setwd(workspace)
color1 <- "#DB6D00"
color2 <- "#070092"
color3 <- "#ffff99" # yellow
  

file_NCBItoNCBI <- paste(workspace, "/free_text/results_trainNCBI_testNCBI_2018-04-16_08_57_20.csv", sep="")
file_NCBItoEBI <- paste(workspace, "/free_text/results_trainNCBI_testEBI_2018-04-16_19_11_51.csv", sep="")
file_EBItoEBI <- paste(workspace, "/free_text/results_trainEBI_testEBI_2018-04-16_23_59_03.csv", sep="")
file_EBItoNCBI <- paste(workspace, "/free_text/results_trainEBI_testNCBI_2018-04-17_06_53_04.csv", sep="")

file_NCBItoNCBI_annotated <- paste(workspace, "/annotated/results_trainNCBI_testNCBI_annotated_2018-04-17_09_13_57.csv", sep="")
file_NCBItoEBI_annotated <- paste(workspace, "/annotated/results_trainNCBI_testEBI_annotated_2018-04-17_18_06_15.csv", sep="")
file_EBItoEBI_annotated <- paste(workspace, "/annotated/results_trainEBI_testEBI_annotated_2018-04-17_20_37_23.csv", sep="")
file_EBItoNCBI_annotated <- paste(workspace, "/annotated/results_trainEBI_testNCBI_annotated_2018-04-17_22_43_26.csv", sep="")

# file_NCBItoNCBI_annotated_mappings <- paste(workspace, "/annotated_mappings/results_trainNCBI_testNCBI_annotated_mappings_2018-04-18_05_30_09.csv", sep="")
# file_NCBItoEBI_annotated_mappings <- paste(workspace, "/annotated_mappings/results_trainNCBI_testEBI_annotated_mappings_2018-04-18_07_40_04.csv", sep="")
# file_EBItoEBI_annotated_mappings <- paste(workspace, "/annotated_mappings/results_trainEBI_testEBI_annotated_mappings_2018-04-18_03_31_33.csv", sep="")
# file_EBItoNCBI_annotated_mappings <- paste(workspace, "/annotated_mappings/results_trainEBI_testNCBI_annotated_mappings_2018-04-18_01_11_03.csv", sep="")

file_NCBItoNCBI_annotated_mappings <- paste(workspace, "/results_trainNCBI_testNCBI_annotated_mappings_2018-04-19_10_58_07.csv", sep="")
file_NCBItoEBI_annotated_mappings <- paste(workspace, "/results_trainNCBI_testEBI_annotated_mappings-partial_2018-04-19_08_27_30.csv", sep="")
file_EBItoEBI_annotated_mappings <- paste(workspace, "/results_trainEBI_testEBI_annotated_mappings_2018-04-19_07_06_18.csv", sep="")
file_EBItoNCBI_annotated_mappings <- paste(workspace, "/results_trainEBI_testNCBI_annotated_mappings_2018-04-19_07_29_00.csv", sep="")




### The following inputs are just for testing

# file_NCBItoNCBI <- paste(workspace, "/mini/results_trainNCBI_testNCBI_2018-04-16_08_57_20.csv", sep="")
# file_NCBItoEBI <- paste(workspace, "/mini/results_trainNCBI_testEBI_2018-04-16_19_11_51.csv", sep="")
# file_EBItoEBI <- paste(workspace, "/mini/results_trainEBI_testEBI_2018-04-16_23_59_03.csv", sep="")
# file_EBItoNCBI <- paste(workspace, "/mini/results_trainEBI_testNCBI_2018-04-17_06_53_04.csv", sep="")
# 
# file_NCBItoNCBI_annotated <- paste(workspace, "/mini/results_trainNCBI_testNCBI_annotated_2018-04-17_09_13_57.csv", sep="")
# file_NCBItoEBI_annotated <- paste(workspace, "/mini/results_trainNCBI_testEBI_annotated_2018-04-17_18_06_15.csv", sep="")
# file_EBItoEBI_annotated <- paste(workspace, "/mini/results_trainEBI_testEBI_annotated_2018-04-17_20_37_23.csv", sep="")
# file_EBItoNCBI_annotated <- paste(workspace, "/mini/results_trainEBI_testNCBI_annotated_2018-04-17_22_43_26.csv", sep="")
# 
# file_NCBItoNCBI_annotated_mappings <- paste(workspace, "/mini/results_trainNCBI_testNCBI_annotated_mappings_2018-04-18_05_30_09.csv", sep="")
# file_NCBItoEBI_annotated_mappings <- paste(workspace, "/mini/results_trainEBI_testEBI_annotated_mappings_2018-04-18_03_31_33.csv", sep="")
# file_EBItoEBI_annotated_mappings <- paste(workspace, "/mini/results_trainEBI_testEBI_annotated_mappings_2018-04-18_03_31_33.csv", sep="")
# file_EBItoNCBI_annotated_mappings <- paste(workspace, "/mini/results_trainEBI_testNCBI_annotated_mappings_2018-04-18_01_11_03.csv", sep="")

### FUNCTION DEFINITIONS ###

# Aggregation by no_populated_fields
aggregate_data_1 <- function(df, reciprocal_rank_vr_column, reciprocal_rank_baseline_column) {
  # aggregation for the 'recommender' method
  agg1 <- aggregate(list(mrr=df[[reciprocal_rank_vr_column]]), by=list(no_populated_fields = df$populated_fields_size), FUN=mean)
  agg1$method <- "recommender"
  # aggregation for the 'baseline' method
  agg2 <- aggregate(list(mrr=df[[reciprocal_rank_baseline_column]]), by=list(no_populated_fields = df$populated_fields_size), FUN=mean)
  agg2$method <- "baseline"
  # final aggregation
  agg_final <- rbind(agg1, agg2)
  # Limit it to no_populated_fields <5
  agg_final <- agg_final[agg_final$no_populated_fields < 5,]
  agg_final$experiment <- df$experiment[1]
  return(agg_final)
}

# Aggregation by no_populated_fields
aggregate_data_1_2 <- function(df, reciprocal_rank_vr_column, reciprocal_rank_baseline_column, recom_method_name="recommender", baseline_method_name="baseline") {
  # aggregation for the 'recommender' method
  agg1 <- aggregate(list(mrr=df[[reciprocal_rank_vr_column]]), by=list(no_populated_fields = df$populated_fields_size), FUN=mean)
  agg1$method <- recom_method_name
  if (!is.null(reciprocal_rank_baseline_column)) {
    # aggregation for the 'baseline' method
    agg2 <- aggregate(list(mrr=df[[reciprocal_rank_baseline_column]]), by=list(no_populated_fields = df$populated_fields_size), FUN=mean)
    agg2$method <- "baseline"
    # final aggregation
    agg_final <- rbind(agg1, agg2)
  }
  else {
    agg_final <- agg1
  }
  # Limit it to no_populated_fields <5
  agg_final <- agg_final[agg_final$no_populated_fields < 5,]
  agg_final$experiment <- df$experiment[1]
  return(agg_final)
}

# Aggregation by target_field and no_populated_fields
aggregate_data_2 <- function(df, reciprocal_rank_vr_column, reciprocal_rank_baseline_column) {
  # aggregation for the 'recommender' method
  agg1 <- aggregate(list(mrr=df[[reciprocal_rank_vr_column]]), by=list(field = df$target_field, no_populated_fields = df$populated_fields_size), FUN=mean)
  agg1$method <- "recommender"
  # aggregation for the 'baseline' method
  agg2 <- aggregate(list(mrr=df[[reciprocal_rank_baseline_column]]), by=list(field = df$target_field, no_populated_fields = df$populated_fields_size), FUN=mean)
  agg2$method <- "baseline"
  # final aggregation
  agg_final <- rbind(agg1, agg2)
  # Limit it to no_populated_fields <5
  agg_final <- agg_final[agg_final$no_populated_fields < 5,]
  agg_final$experiment <- df$experiment[1]
  return(agg_final)
}

# Generate MRR plot (Recommender vs Baseline)
# generate_plot <- function(df, title="title"){
#   plot <- ggplot(data=df, aes(x=no_populated_fields, y=mrr, group=method, colour=method)) + 
#     geom_line() + geom_point() + geom_text(aes(label=sprintf("%0.2f", round(mrr, digits = 2))), vjust=2, show.legend = FALSE) +
#     ylim(0,1) + ggtitle(title) + xlab("No. populated fields") + ylab("Mean Reciprocal Rank") 
#   # + scale_color_brewer(palette="Dark2")
#   return(plot)
# }

generate_plot <- function(df, title="title"){
  plot <- ggplot(data=df, aes(x=no_populated_fields, y=mrr, group=method, colour=method)) + 
    geom_line(aes(linetype=method), size=0.7) + 
    scale_linetype_manual(values=c("solid", "solid")) +
    scale_color_manual(values=c(color1, color2)) +
    geom_point() + geom_text(size=2.5, aes(label=sprintf("%0.2f", round(mrr, digits = 2))), vjust=2, show.legend = FALSE) +
    ylim(0,1) + ggtitle(title) + xlab("No. populated fields") + ylab("Mean Reciprocal Rank") +
    theme(text = element_text(size=8))
  # + scale_color_brewer(palette="Dark2")
  return(plot)
}

generate_plot_2 <- function(df, title="title"){
  plot <- ggplot(data=df, aes(x=no_populated_fields, y=mrr, group=method, colour=method)) + 
    geom_line(aes(linetype=method), size=0.7) + 
    scale_linetype_manual(values=c("dotted", "dashed", "solid")) +
    scale_color_manual(values=c(color2, color2, color2)) +
    geom_point() + 
    #geom_text(size=2.5, aes(label=sprintf("%0.2f", round(mrr, digits = 2))), vjust=2, show.legend = FALSE) +
    ylim(0,1) + ggtitle(title) + xlab("No. populated fields") + ylab("Mean Reciprocal Rank") +
    theme(text = element_text(size=8))
  # + scale_color_brewer(palette="Dark2")
  return(plot)
}

# Generate MRR plot (Recommender vs Baseline) per field
# generate_plot_field <- function(df, title="title"){
#   plot <- ggplot(data=df, aes(x=field, y=mrr, fill=method)) + geom_bar(stat="identity", position=position_dodge()) +
#     ylim(0,1) + ggtitle(title) + xlab("Field") + ylab("Mean Reciprocal Rank") 
#   return(plot)
# }

generate_plot_field <- function(df, title="title"){
  plot <- ggplot(data=df, aes(x=field, y=mrr, fill=method)) + geom_bar(stat="identity", position=position_dodge()) +
    scale_fill_manual(values=c(color1, color2)) +
    ylim(0,1) + ggtitle(title) + xlab("Field") + ylab("Mean Reciprocal Rank") +
    theme(text = element_text(size=8))
  return(plot)
}

setClass("EvaluationSet", representation(datasets = "vector", description = "character"))

generate_all_plots <- function(evaluation_set, reciprocal_rank_vr_column, reciprocal_rank_baseline_column) {
  
  data_NCBItoNCBI <- read.csv(evaluation_set@datasets[1])
  data_NCBItoEBI <- read.csv(evaluation_set@datasets[2])
  data_EBItoEBI <- read.csv(evaluation_set@datasets[3])
  data_EBItoNCBI <- read.csv(evaluation_set@datasets[4])
  description <- evaluation_set@description
  
  # remove the 'treatment' field from the analysis
  data_NCBItoNCBI <- data_NCBItoNCBI[data_NCBItoNCBI$target_field!="treatment",]
  
  data_NCBItoNCBI$experiment <- "NCBItoNCBI"
  data_NCBItoEBI$experiment <- "NCBItoEBI"
  data_EBItoEBI$experiment <- "EBItoEBI"
  data_EBItoNCBI$experiment <- "EBItoNCBI"
  
  #hist(data_NCBItoNCBI$populated_fields_size)
  
  # 1) Recommender vs Baseline 2x2 plots
  p1 <- generate_plot(aggregate_data_1(data_NCBItoNCBI, reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: NCBI; Testing: NCBI")
  p2 <- generate_plot(aggregate_data_1(data_NCBItoEBI, reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: NCBI; Testing: EBI")
  p3 <- generate_plot(aggregate_data_1(data_EBItoEBI, reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: EBI; Testing: EBI")
  p4 <- generate_plot(aggregate_data_1(data_EBItoNCBI, reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: EBI; Testing: NCBI")
  fig1 <- ggarrange(p1, p2, p3, p4, ncol=2, nrow=2, common.legend = TRUE, legend="bottom")
  desc_text <- paste("Metadata Recommender vs Baseline (", description, ")", sep = "")
  fig1_annotated <- annotate_figure(fig1, top = text_grob(label=desc_text, color = "black", face = "bold", size = 11))
  print(fig1_annotated)
  
  # Export plot
  dev.copy(pdf, paste("plot1_", gsub(" ", "_", description), "_", format(Sys.time(), "%Y_%m_%d_%H_%M_%S"), ".pdf", sep=""))
  dev.off()
  
  # 2) Recommender vs Baseline per target field
  p1 <- generate_plot_field(aggregate_data_2(data_NCBItoNCBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: NCBI; Testing: NCBI")
  p2 <- generate_plot_field(aggregate_data_2(data_NCBItoEBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: NCBI; Testing: EBI")
  p3 <- generate_plot_field(aggregate_data_2(data_EBItoEBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: EBI; Testing: EBI")
  p4 <- generate_plot_field(aggregate_data_2(data_EBItoNCBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: EBI; Testing: NCBI")
  fig2 <- ggarrange(p1, p2, p3, p4, ncol=2, nrow=2, common.legend = TRUE, legend="bottom")
  desc_text <- paste("Metadata Recommender vs Baseline by field (", description, ")", sep = "")
  fig2_annotated <- annotate_figure(fig2, top = text_grob(label=desc_text, color = "black", face = "bold", size = 11))
  print(fig2_annotated)
  
  # Export plot
  dev.copy(pdf, paste("plot2_", gsub(" ", "_", description), "_", format(Sys.time(), "%Y_%m_%d_%H_%M_%S"), ".pdf", sep=""))
  dev.off()
  
  # histogram with positions of correct values
  #ggplot(data_NCBItoNCBI, aes(x=correct_pos_vr)) + geom_histogram()
  
}

generate_all_plots_overlapped <- function(evaluation_set1, evaluation_set2, evaluation_set3, reciprocal_rank_vr_column, reciprocal_rank_baseline_column) {
  
  data_NCBItoNCBI1 <- read.csv(evaluation_set1@datasets[1])
  data_NCBItoEBI1 <- read.csv(evaluation_set1@datasets[2])
  data_EBItoEBI1 <- read.csv(evaluation_set1@datasets[3])
  data_EBItoNCBI1 <- read.csv(evaluation_set1@datasets[4])
  description1 <- evaluation_set1@description
  
  data_NCBItoNCBI2 <- read.csv(evaluation_set2@datasets[1])
  data_NCBItoEBI2 <- read.csv(evaluation_set2@datasets[2])
  data_EBItoEBI2 <- read.csv(evaluation_set2@datasets[3])
  data_EBItoNCBI2 <- read.csv(evaluation_set2@datasets[4])
  description2 <- evaluation_set2@description
  
  data_NCBItoNCBI3 <- read.csv(evaluation_set3@datasets[1])
  data_NCBItoEBI3 <- read.csv(evaluation_set3@datasets[2])
  data_EBItoEBI3 <- read.csv(evaluation_set3@datasets[3])
  data_EBItoNCBI3 <- read.csv(evaluation_set3@datasets[4])
  description3 <- evaluation_set3@description
  
  data_NCBItoNCBI1$experiment <- "NCBItoNCBI"
  data_NCBItoEBI1$experiment <- "NCBItoEBI"
  data_EBItoEBI1$experiment <- "EBItoEBI"
  data_EBItoNCBI1$experiment <- "EBItoNCBI"
  
  data_NCBItoNCBI2$experiment <- "NCBItoNCBI"
  data_NCBItoEBI2$experiment <- "NCBItoEBI"
  data_EBItoEBI2$experiment <- "EBItoEBI"
  data_EBItoNCBI2$experiment <- "EBItoNCBI"
  
  data_NCBItoNCBI3$experiment <- "NCBItoNCBI"
  data_NCBItoEBI3$experiment <- "NCBItoEBI"
  data_EBItoEBI3$experiment <- "EBItoEBI"
  data_EBItoNCBI3$experiment <- "EBItoNCBI"
  
  data_p1_1 <- aggregate_data_1_2(data_NCBItoNCBI1, reciprocal_rank_vr_column, NULL, recom_method_name="recommender", baseline_method_name="baseline")
  data_p1_2 <- aggregate_data_1_2(data_NCBItoNCBI2, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated", baseline_method_name="baseline_annotated")
  data_p1_3 <- aggregate_data_1_2(data_NCBItoNCBI3, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated_mappings", baseline_method_name="baseline_annotated_mappings")
  data_p1 <- rbind(data_p1_1, data_p1_2, data_p1_3)
  
  data_p2_1 <- aggregate_data_1_2(data_NCBItoEBI1, reciprocal_rank_vr_column, NULL, recom_method_name="recommender", baseline_method_name="baseline")
  data_p2_2 <- aggregate_data_1_2(data_NCBItoEBI2, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated", baseline_method_name="baseline_annotated")
  data_p2_3 <- aggregate_data_1_2(data_NCBItoEBI3, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated_mappings", baseline_method_name="baseline_annotated_mappings")
  data_p2 <- rbind(data_p2_1, data_p2_2, data_p2_3)
  
  data_p3_1 <- aggregate_data_1_2(data_EBItoEBI1, reciprocal_rank_vr_column, NULL, recom_method_name="recommender", baseline_method_name="baseline")
  data_p3_2 <- aggregate_data_1_2(data_EBItoEBI2, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated", baseline_method_name="baseline_annotated")
  data_p3_3 <- aggregate_data_1_2(data_EBItoEBI3, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated_mappings", baseline_method_name="baseline_annotated_mappings")
  data_p3 <- rbind(data_p3_1, data_p3_2, data_p3_3)
  
  data_p4_1 <- aggregate_data_1_2(data_EBItoNCBI1, reciprocal_rank_vr_column, NULL, recom_method_name="recommender", baseline_method_name="baseline")
  data_p4_2 <- aggregate_data_1_2(data_EBItoNCBI2, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated", baseline_method_name="baseline_annotated")
  data_p4_3 <- aggregate_data_1_2(data_EBItoNCBI3, reciprocal_rank_vr_column, NULL, recom_method_name="recommender_annotated_mappings", baseline_method_name="baseline_annotated_mappings")
  data_p4 <- rbind(data_p4_1, data_p4_2, data_p4_3)

  # 1) Recommender vs Baseline 2x2 plots
  p1 <- generate_plot_2(data_p1, "Training: NCBI; Testing: NCBI")
  p2 <- generate_plot_2(data_p2, "Training: NCBI; Testing: EBI")
  p3 <- generate_plot_2(data_p3, "Training: EBI; Testing: EBI")
  p4 <- generate_plot_2(data_p4, "Training: EBI; Testing: NCBI")
  fig1 <- ggarrange(p1, p2, p3, p4, ncol=2, nrow=2, common.legend = TRUE, legend="bottom")
  description = paste(description1, " vs ", description2, sep = "")
  desc_text <- paste("Metadata Recommender (text vs annotated vs annotated_mappings)", sep = "")
  fig1_annotated <- annotate_figure(fig1, top = text_grob(label=desc_text, color = "black", face = "bold", size = 11))
  print(fig1_annotated)

  # Export plot
  dev.copy(pdf, paste("plot3_", gsub(" ", "_", description), "_", format(Sys.time(), "%Y_%m_%d_%H_%M_%S"), ".pdf", sep=""))
  dev.off()

}

### MAIN BODY ###

evaluation_set_1 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI, file_NCBItoEBI, file_EBItoEBI, file_EBItoNCBI), description="free text")
evaluation_set_2 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_annotated, file_NCBItoEBI_annotated, file_EBItoEBI_annotated, file_EBItoNCBI_annotated), description="annotated")
evaluation_set_3 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_annotated_mappings, file_NCBItoEBI_annotated_mappings, file_EBItoEBI_annotated_mappings, file_EBItoNCBI_annotated_mappings), description="annotated-mappings")

evaluation_sets = c(evaluation_set_1, evaluation_set_2, evaluation_set_3)

# for (evaluation_set in evaluation_sets){
#   generate_all_plots(evaluation_set, 'RR_top5_vr', 'RR_top5_baseline')
# }

generate_all_plots_overlapped(evaluation_set_1, evaluation_set_2, evaluation_set_3, 'RR_top5_vr', 'RR_top5_baseline')

################################

# hist(data_NCBItoNCBI$populated_fields_size)
# hist(data_NCBItoEBI$populated_fields_size)
