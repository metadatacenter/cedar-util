
library(RWeka)

base_input_path <- '/Users/marcosmr/tmp/ARM_resources/EVALUATION/arff files'
base_output_path <- '/Users/marcosmr/tmp/ARM_resources/EVALUATION/most_frequent_values'

# Free text values
ncbi_arff_file_path <- paste(base_input_path, "/ncbi_training_eef6f399-aa4e-4982-ab04-ad8e9635aa91.arff", sep="")
ebi_arff_file_path <- paste(base_input_path, "/ebi_training_6b6c76e6-1d9b-4096-9702-133e25ecd140.arff", sep="")

# Annotated values
ncbi_annotated_arff_file_path <- paste(base_input_path, "/ncbi_annotated_training_eef6f399-aa4e-4982-ab04-ad8e9635aa91.arff", sep="")
ebi_annotated_arff_file_path <- paste(base_input_path, "/ebi_annotated_training_6b6c76e6-1d9b-4096-9702-133e25ecd140.arff", sep="")

### Functions ###

most_frequent_values <- function(dataset, max_positions = 10, output_file_path, annotated) {
  result <- ''
  for (var in names(dataset)) {
    separator <- '\\]\\('
    pos_separator <- regexpr(pattern = separator, var)
    var_name <- substr(var, pos_separator + 2, nchar(var) - 1)
    values_string <- "["
    for (i in 1:max_positions) {
      value_full <- names(sort(table(dataset[var]), decreasing = TRUE)[i])[1]
      pos_separator <- regexpr(pattern = separator, value_full)
      if (annotated==FALSE) {
        value <- substr(value_full, start=pos_separator+2, stop=nchar(value_full)-1)
      }
      else {
        value <- substr(value_full, start=2, stop=pos_separator-1)
      }
      values_string <- paste(values_string, "\"", value, "\"", ",", sep = "")
    }
    values_string <- substr(values_string, 1, nchar(values_string) - 1)
    values_string <- paste(values_string, "],", sep = "")
    result <- paste(result, "\"", var_name, "\":", values_string, sep = "")
  }
  result <- substr(result, 1, nchar(result) - 1)
  result <- paste("{", result, "}", sep = "")
  write(result, output_file_path)
}

### Main program ###

print_ncbi = TRUE
print_ebi = TRUE
print_ncbi_annotated = TRUE
print_ebi_annotated = TRUE

ncbi_data <- read.arff(ncbi_arff_file_path)
ebi_data <- read.arff(ebi_arff_file_path)
ncbi_annotated_data <- read.arff(ncbi_annotated_arff_file_path)
ebi_annotated_data <- read.arff(ebi_annotated_arff_file_path)

if (print_ncbi) {
  print('*** NCBI (FREE TEXT) - MOST COMMON VALUES ***')
  most_frequent_values(ncbi_data, output_file_path = paste(base_output_path, "/ncbi_frequent_values.json", sep=""), annotated=FALSE)
}
if (print_ebi) {
  print('*** EBI (FREE TEXT) - MOST COMMON VALUES ***')
  most_frequent_values(ebi_data, output_file_path = paste(base_output_path, "/ebi_frequent_values.json", sep=""), annotated=FALSE)
}
if (print_ncbi_annotated) {
  print('*** NCBI (ANNOTATED) - MOST COMMON VALUES ***')
  most_frequent_values(ncbi_annotated_data, output_file_path = paste(base_output_path, "/ncbi_annotated_frequent_values.json", sep=""), annotated=TRUE)
}
if (print_ebi_annotated) {
  print('*** EBI (ANNOTATED) - MOST COMMON VALUES ***')
  most_frequent_values(ebi_annotated_data, output_file_path = paste(base_output_path, "/ebi_annotated_frequent_values.json", sep=""), annotated=TRUE)
}

# Count no. different values - NCBI
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/48197c87-87f2-4f80-954a-e16254849e00](sex)`))
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/057fec02-39ff-43b1-992e-367938126165](tissue)`))
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/46993fe0-f12e-45bd-adef-39411b7b7c3e](cell_line)`))
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/5d8aa75b-3550-46d0-bbfb-9006f16e3785](cell_type)`))
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/0ced2f97-033d-4501-8a55-c6c3aa7a7c05](disease)`))
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/e5e91294-cbfe-4730-a0fd-438e8c2e04b4](ethnicity)`))
# dim(table(ncbi_data$`[https://repo.metadatacenter.orgx/template-fields/67ebeb3c-0f6b-4b7e-b453-3c7c93048f44](treatment)`))

# Count no. different values - EBI
# dim(table(ebi_data$`[https://repo.metadatacenter.orgx/template-fields/5bb59e46-5110-4f2a-8057-23ee0bc2d468](sex)`))
# dim(table(ebi_data$`[https://repo.metadatacenter.orgx/template-fields/aef8767b-a5c1-45d7-b33b-6235a6e0cfab](organismPart)`))
# dim(table(ebi_data$`[https://repo.metadatacenter.orgx/template-fields/16652eb0-5b20-41c7-b4aa-80b07ad872fc](cellLine)`))
# dim(table(ebi_data$`[https://repo.metadatacenter.orgx/template-fields/bef0a12b-bf69-43f7-ac6f-8c3d8093c20a](cellType)`))
# dim(table(ebi_data$`[https://repo.metadatacenter.orgx/template-fields/7a3d91e1-a5ab-48e4-9bd6-38f6d04f92fa](diseaseState)`))
# dim(table(ebi_data$`[https://repo.metadatacenter.orgx/template-fields/cea0e329-8899-4e9e-9ed5-647c8c0c0fba](ethnicity)`))
