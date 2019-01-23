# Analysis of ARM results

library(ggplot2)
library(gridExtra)
library(ggpubr)
#library(wesanderson)
library("RColorBrewer")


### CONSTANTS ###
workspace = "/Users/marcosmr/tmp/ARM_resources/evaluation_results"
setwd(workspace)

file_NCBItoNCBI <- paste(workspace, "/2018_03_27_3-training_124200_ncbi-testing-13800_ncbi_NOSTRICT_BASELINE/results_train-NCBI_instances_test-NCBI_13800instances_2018-03-28_02_39_01.csv", sep="")
file_NCBItoEBI <- paste(workspace, "/2018_03_27_4-training_124200_ncbi-testing-13800_ebi_NOSTRICT_BASELINE/results_train-NCBI_instances_test-EBI_13800instances_2018-03-28_03_25_13.csv", sep="")
file_EBItoEBI <- paste(workspace, "/2018_03_27_5-training_124200_ebi-testing-13800_ebi_NOSTRICT_BASELINE/results_train-EBI_instances_test-EBI_13800instances_2018-03-28_04_12_02.csv", sep="")
file_EBItoNCBI <- paste(workspace, "/2018_03_27_6-training_124200_ebi-testing-13800_ncbi_NOSTRICT_BASELINE/results_train-EBI_instances_test-NCBI_13800instances_2018-03-28_05_00_58.csv", sep="")

file_NCBItoNCBI_annotated <- paste(workspace, "/2018-04-10_ANNOTATED_INSTANCES/results_train-NCBI_instances_test-NCBI_13800instances_2018-04-10_00_00_23.csv", sep="")
file_NCBItoEBI_annotated <- paste(workspace, "/2018-04-10_ANNOTATED_INSTANCES/results_train-NCBI_instances_test-EBI_13800instances_2018-04-10_19_43_29.csv", sep="")
file_EBItoEBI_annotated <- paste(workspace, "/2018-04-10_ANNOTATED_INSTANCES/results_train-EBI_instances_test-EBI_13800instances_2018-04-10_17_11_27.csv", sep="")
file_EBItoNCBI_annotated <- paste(workspace, "/2018-04-10_ANNOTATED_INSTANCES/results_train-EBI_instances_test-NCBI_13800instances_2018-04-10_18_59_36.csv", sep="")

file_NCBItoNCBI_annotated_allpopulatedsets <- paste(workspace, "/results_train-NCBI_instances_test-NCBI_2000instances_2018-04-10_22_36_11.csv", sep="")
file_NCBItoEBI_annotated_allpopulatedsets <- paste(workspace, "/results_train-NCBI_instances_test-EBI_1000instances_2018-04-10_23_09_10.csv", sep="")
file_EBItoEBI_annotated_allpopulatedsets <- paste(workspace, "/results_train-EBI_instances_test-EBI_1000instances_2018-04-10_23_22_10.csv", sep="")
file_EBItoNCBI_annotated_allpopulatedsets <- paste(workspace, "/results_train-EBI_instances_test-NCBI_1000instances_2018-04-10_23_31_28.csv", sep="")

file_NCBItoNCBI_annotated_allpopulatedsets_mappings <- paste(workspace, "/2018-04-12_ANNOTATED_POPULATED_MAPPINGS/results_train-NCBI_instances_test-NCBI_13800instances_2018-04-12_02_35_21.csv", sep="")
file_NCBItoEBI_annotated_allpopulatedsets_mappings <- paste(workspace, "/2018-04-12_ANNOTATED_POPULATED_MAPPINGS/results_train-NCBI_instances_test-EBI_13800instances_2018-04-12_04_20_03.csv", sep="")
file_EBItoEBI_annotated_allpopulatedsets_mappings <- paste(workspace, "/2018-04-12_ANNOTATED_POPULATED_MAPPINGS/results_train-NCBI_instances_test-EBI_13800instances_2018-04-12_04_20_03.csv", sep="")
file_EBItoNCBI_annotated_allpopulatedsets_mappings <- paste(workspace, "/2018-04-12_ANNOTATED_POPULATED_MAPPINGS/results_train-NCBI_instances_test-EBI_13800instances_2018-04-12_04_20_03.csv", sep="")


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
generate_plot <- function(df, title="title"){
  plot <- ggplot(data=df, aes(x=no_populated_fields, y=mrr, group=method, colour=method)) + 
    geom_line() + geom_point() + geom_text(aes(label=sprintf("%0.2f", round(mrr, digits = 2))), vjust=2, show.legend = FALSE) +
    ylim(0,1) + ggtitle(title) + xlab("No. populated fields") + ylab("Mean Reciprocal Rank") 
  # + scale_color_brewer(palette="Dark2")
  return(plot)
}

# Generate MRR plot (Recommender vs Baseline) per field
generate_plot_field <- function(df, title="title"){
  plot <- ggplot(data=df, aes(x=field, y=mrr, fill=method)) + geom_bar(stat="identity", position=position_dodge()) +
    ylim(0,1) + ggtitle(title) + xlab("Field") + ylab("Mean Reciprocal Rank") 
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
  fig1_annotated <- annotate_figure(fig1, top = text_grob(label=desc_text, color = "red", face = "bold", size = 14))
  print(fig1_annotated)
  
  # Export plot
  dev.copy(png, paste("plot1_", gsub(" ", "_", description), "_", format(Sys.time(), "%Y_%m_%d_%H_%M_%S"), ".png", sep=""), width=800,height=700)
  dev.off()
  
  # 2) Recommender vs Baseline per target field
  p1 <- generate_plot_field(aggregate_data_2(data_NCBItoNCBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: NCBI; Testing: NCBI")
  p2 <- generate_plot_field(aggregate_data_2(data_NCBItoEBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: NCBI; Testing: EBI")
  p3 <- generate_plot_field(aggregate_data_2(data_EBItoEBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: EBI; Testing: EBI")
  p4 <- generate_plot_field(aggregate_data_2(data_EBItoNCBI,reciprocal_rank_vr_column, reciprocal_rank_baseline_column), "Training: EBI; Testing: NCBI")
  fig2 <- ggarrange(p1, p2, p3, p4, ncol=2, nrow=2, common.legend = TRUE, legend="bottom")
  desc_text <- paste("Metadata Recommender vs Baseline by field (", description, ")", sep = "")
  fig2_annotated <- annotate_figure(fig2, top = text_grob(label=desc_text, color = "red", face = "bold", size = 14))
  print(fig2_annotated)
  
  # Export plot
  dev.copy(png, paste("plot2_", gsub(" ", "_", description), "_", format(Sys.time(), "%Y_%m_%d_%H_%M_%S"), ".png", sep=""), width=800,height=700)
  dev.off()
  
  # histogram with positions of correct values
  #ggplot(data_NCBItoNCBI, aes(x=correct_pos_vr)) + geom_histogram()
  
}

### MAIN BODY ###

evaluation_set_1 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI, file_NCBItoEBI, file_EBItoEBI, file_EBItoNCBI), description="free text")
evaluation_set_2 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_annotated, file_NCBItoEBI_annotated, file_EBItoEBI_annotated, file_EBItoNCBI_annotated), description="annotated")
evaluation_set_3 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_annotated_allpopulatedsets, file_NCBItoEBI_annotated_allpopulatedsets, 
                                                    file_EBItoEBI_annotated_allpopulatedsets, file_EBItoNCBI_annotated_allpopulatedsets), description="annotated and populated sets")
evaluation_set_4 <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_annotated_allpopulatedsets_mappings, file_NCBItoEBI_annotated_allpopulatedsets_mappings, 
                                                    file_EBItoEBI_annotated_allpopulatedsets_mappings, file_EBItoNCBI_annotated_allpopulatedsets_mappings), description="annotated - populated - mappings")

#evaluation_sets = c(evaluation_set_1, evaluation_set_2, evaluation_set_4)
evaluation_sets = c(evaluation_set_1)

for (evaluation_set in evaluation_sets){
  generate_all_plots(evaluation_set, 'RR_vr', 'RR_baseline')
}
#######
# generate_all_plots(evaluation_sets[3])
# 
# evaluation_set <- evaluation_set_3
# 
# data_NCBItoNCBI <- read.csv(evaluation_set@datasets[1])
# data_NCBItoEBI <- read.csv(evaluation_set@datasets[2])
# data_EBItoEBI <- read.csv(evaluation_set@datasets[3])
# data_EBItoNCBI <- read.csv(evaluation_set@datasets[4])
# 
# 
# # remove the 'treatment' field from the analysis
# data_NCBItoNCBI <- data_NCBItoNCBI[data_NCBItoNCBI$target_field!="treatment",]
# 
# data_NCBItoNCBI$experiment <- "NCBItoNCBI"
# data_NCBItoEBI$experiment <- "NCBItoEBI"
# data_EBItoEBI$experiment <- "EBItoEBI"
# data_EBItoNCBI$experiment <- "EBItoNCBI"
# 
# 
# hist(data_NCBItoNCBI$populated_fields_size)
# hist(data_NCBItoEBI$populated_fields_size)

#########

# file_NCBItoNCBI_RRs <- paste(workspace, "/results_train-NCBI_instances_test-NCBI_5000instances_2018-04-12_19_34_43.csv", sep="")
# 
# 
# evaluation_set_x <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_RRs, file_NCBItoNCBI_RRs,
#                                                     file_NCBItoNCBI_RRs, file_NCBItoNCBI_RRs), description=paste('RR_top3_vr', 'RR_top3_baseline',sep="-"))
# generate_all_plots(evaluation_set_x, 'RR_top3_vr', 'RR_top3_baseline')
# 
# evaluation_set_x <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_RRs, file_NCBItoNCBI_RRs,
#                                                     file_NCBItoNCBI_RRs, file_NCBItoNCBI_RRs), description=paste('RR_top5_vr', 'RR_top5_baseline',sep="-"))
# generate_all_plots(evaluation_set_x, 'RR_top5_vr', 'RR_top5_baseline')
# 
# evaluation_set_x <- new("EvaluationSet", datasets=c(file_NCBItoNCBI_RRs, file_NCBItoNCBI_RRs,
#                                                     file_NCBItoNCBI_RRs, file_NCBItoNCBI_RRs), description=paste('RR_top10_vr', 'RR_top10_baseline',sep="-"))
# generate_all_plots(evaluation_set_x, 'RR_top10_vr', 'RR_top10_baseline')







