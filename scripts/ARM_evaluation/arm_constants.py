#!/usr/bin/python3

from enum import Enum

class BIOSAMPLES_DB(Enum):
    NCBI = 1
    EBI = 2

BASE_PATH = "/Users/marcosmr/tmp/ARM_resources/EVALUATION"

####################
# DOWNLOAD SAMPLES #
####################

# Input parameters for 'ebi_biosamples_1_download_split.py'
EBI_DOWNLOAD_URL = 'https://www.ebi.ac.uk/biosamples/api/samples'
EBI_DOWNLOAD_MAX_SIZE_PER_PAGE = 1000
EBI_DOWNLOAD_PAGES_PER_FILE = 1
EBI_DOWNLOAD_MAX_PAGES = -1
EBI_DOWNLOAD_OUTPUT_FOLDER = BASE_PATH + "/samples/ebi_samples/original"

##################
# FILTER SAMPLES #
##################

# Input parameters for 'ncbi_biosamples_2_filter.py'
NCBI_FILTER_INPUT_FILE = BASE_PATH + '/samples/ncbi_samples/original/2018-03-09-biosample_set.xml'
NCBI_FILTER_OUTPUT_FILE = BASE_PATH + '/samples/ncbi_samples/filtered/biosample_result_filtered.xml'
NCBI_FILTER_RELEVANT_ATTS = ['sex', 'tissue', 'disease', 'cell_type', 'cell type' 'cell_line', 'cell line', 'ethnicity']
NCBI_FILTER_MIN_RELEVANT_ATTS = 3

# Input parameters for 'ebi_biosamples_2_filter.py'
EBI_FILTER_INPUT_FOLDER = BASE_PATH + '/samples/ebi_samples/original'
EBI_FILTER_OUTPUT_FOLDER = BASE_PATH + '/samples/ebi_samples/filtered'
EBI_FILTER_MAX_SAMPLES_PER_FILE = 10000
EBI_FILTER_RELEVANT_ATTS = ['sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState', 'ethnicity']
EBI_FILTER_MIN_RELEVANT_ATTS = 3

############################
# GENERATE CEDAR INSTANCES #
############################

# Input parameters for 'ebi_biosamples_3_to_cedar_instances.py'
EBI_INSTANCES_TRAINING_SET_SIZE = 102000
EBI_INSTANCES_TESTING_SET_SIZE = 18000
EBI_INSTANCES_MAX_FILES_PER_FOLDER = 10000
EBI_INSTANCES_INPUT_PATH = EBI_FILTER_OUTPUT_FOLDER
EBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ebi_cedar_instances'
EBI_INSTANCES_TRAINING_BASE_PATH = EBI_INSTANCES_OUTPUT_BASE_PATH + '/training'
EBI_INSTANCES_TESTING_BASE_PATH = EBI_INSTANCES_OUTPUT_BASE_PATH + '/testing'
EBI_INSTANCES_EXCLUDE_IDS = False
EBI_INSTANCES_EXCLUDED_IDS_FILE_PATH = None
EBI_INSTANCES_OUTPUT_BASE_FILE_NAME = 'ebi_biosample_instance'
EBI_INSTANCES_EMPTY_BIOSAMPLE_INSTANCE_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ebi/ebi_biosample_instance_empty.json'

# Input parameters for 'ncbi_biosample_2_to_cedar_instances.py'
# NCBI_INSTANCES_TRAINING_SET_SIZE = 102000
# NCBI_INSTANCES_TESTING_SET_SIZE = 0
# NCBI_INSTANCES_MAX_FILES_PER_FOLDER = 10000
# NCBI_INSTANCES_INPUT_PATH = NCBI_FILTER_OUTPUT_FILE
# NCBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ncbi_cedar_instances'
# NCBI_INSTANCES_TRAINING_BASE_PATH = NCBI_INSTANCES_OUTPUT_BASE_PATH + '/training'
# NCBI_INSTANCES_TESTING_BASE_PATH = NCBI_INSTANCES_OUTPUT_BASE_PATH + '/testing'
# NCBI_INSTANCES_EXCLUDE_IDS = True
# NCBI_INSTANCES_EXCLUDED_IDS_FILE_PATH = BASE_PATH + '/cedar_instances/ebi_cedar_instances/testing_ids.txt'
# NCBI_INSTANCES_OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
# NCBI_INSTANCES_EMPTY_BIOSAMPLE_INSTANCE_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ncbi/ncbi_biosample_instance_empty.json'

NCBI_INSTANCES_TRAINING_SET_SIZE = 0
NCBI_INSTANCES_TESTING_SET_SIZE = 18000
NCBI_INSTANCES_MAX_FILES_PER_FOLDER = 10000
NCBI_INSTANCES_INPUT_PATH = NCBI_FILTER_OUTPUT_FILE
NCBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ncbi_cedar_instances'
NCBI_INSTANCES_TRAINING_BASE_PATH = NCBI_INSTANCES_OUTPUT_BASE_PATH + '/training'
NCBI_INSTANCES_TESTING_BASE_PATH = NCBI_INSTANCES_OUTPUT_BASE_PATH + '/testing'
NCBI_INSTANCES_EXCLUDE_IDS = True
NCBI_INSTANCES_EXCLUDED_IDS_FILE_PATH = BASE_PATH + '/cedar_instances/ncbi_ebi_training_ids.txt'
NCBI_INSTANCES_OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
NCBI_INSTANCES_EMPTY_BIOSAMPLE_INSTANCE_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ncbi/ncbi_biosample_instance_empty.json'


##############################################
# SYSTEM EVALUATION (arm_evaluation_main.py) #
##############################################

EVALUATION_TRAINING_INSTANCES_BASE_FOLDERS = {
    "NCBI": BASE_PATH + '/cedar_instances/ncbi_cedar_instances/training',
    "EBI": BASE_PATH + '/cedar_instances/ebi_cedar_instances/training'
}
EVALUATION_TESTING_INSTANCES_BASE_FOLDERS = {
    "NCBI": BASE_PATH + '/cedar_instances/ncbi_cedar_instances/testing',
    "EBI": BASE_PATH + '/cedar_instances/ebi_cedar_instances/testing'
}
EVALUATION_TRAINING_INSTANCES_ANNOTATED_BASE_FOLDERS = {
    "NCBI": BASE_PATH + '/cedar_instances_annotated/ncbi_cedar_instances/training',
    "EBI": BASE_PATH + '/cedar_instances_annotated/ebi_cedar_instances/training'
}
EVALUATION_TESTING_INSTANCES_ANNOTATED_BASE_FOLDERS = {
    "NCBI": BASE_PATH + '/cedar_instances_annotated/ncbi_cedar_instances/testing',
    "EBI": BASE_PATH + '/cedar_instances_annotated/ebi_cedar_instances/testing'
}
EVALUATION_NCBI_MOST_FREQUENT_VALUES_PATH = BASE_PATH + '/most_frequent_values/ncbi_frequent_values.json'
EVALUATION_EBI_MOST_FREQUENT_VALUES_PATH = BASE_PATH + '/most_frequent_values/ebi_frequent_values.json'
EVALUATION_NCBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH = BASE_PATH + '/most_frequent_values/ncbi_annotated_frequent_values.json'
EVALUATION_EBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH = BASE_PATH + '/most_frequent_values/ebi_annotated_frequent_values.json'



























