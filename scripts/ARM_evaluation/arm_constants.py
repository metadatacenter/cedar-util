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

EVALUATION_TRAINING_DB = BIOSAMPLES_DB.NCBI
EVALUATION_TESTING_DB = BIOSAMPLES_DB.NCBI
EVALUATION_USE_ANNOTATED_VALUES = True
EVALUATION_EXTEND_URIS_WITH_MAPPINGS = True
EVALUATION_MAPPINGS_FILE_PATH = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings_merged.json'
EVALUATION_MAX_NUMBER_INSTANCES = 20000
EVALUATION_CEDAR_API_KEY = ''

# EVALUATION_TESTING_INSTANCES_BASE_FOLDERS = {
#     "NCBI": BASE_PATH + '/cedar_instances/ncbi_cedar_instances/testing',
#     "EBI": BASE_PATH + '/cedar_instances/ebi_cedar_instances/testing'
# }

# EVALUATION_TESTING_INSTANCES_ANNOTATED_BASE_FOLDERS = {
#     "NCBI": BASE_PATH + '/cedar_instances_annotated/ncbi_cedar_instances/testing',
#     "EBI": BASE_PATH + '/cedar_instances_annotated/ebi_cedar_instances/testing'
# }

EVALUATION_TESTING_INSTANCES_ANNOTATED_BASE_FOLDERS = {
    "NCBI": BASE_PATH + '/cedar_instances_annotated/ncbi_cedar_instances/testing',
    "EBI": BASE_PATH + '/cedar_instances_annotated/ebi_cedar_instances_different_ontologies/testing'
}

EVALUATION_NCBI_MOST_FREQUENT_VALUES_PATH = BASE_PATH + '/most_frequent_values/ncbi_frequent_values.json'
EVALUATION_EBI_MOST_FREQUENT_VALUES_PATH = BASE_PATH + '/most_frequent_values/ebi_frequent_values.json'
EVALUATION_NCBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH = BASE_PATH + '/most_frequent_values/ncbi_annotated_frequent_values.json'
#EVALUATION_EBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH = BASE_PATH + '/most_frequent_values/ebi_annotated_frequent_values.json'
EVALUATION_EBI_MOST_FREQUENT_VALUES_ANNOTATED_PATH = BASE_PATH + '/most_frequent_values/ebi_annotated_diff_onts_frequent_values.json'

EVALUATION_READ_TEST_INSTANCES_FROM_CEDAR = False  # If false, the instances are read from a local folder
EVALUATION_VR_SERVER = 'https://valuerecommender.metadatacenter.orgx/'
EVALUATION_VR_STRICT_MATCH = False
EVALUATION_NCBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/eef6f399-aa4e-4982-ab04-ad8e9635aa91'
# EVALUATION_EBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/6b6c76e6-1d9b-4096-9702-133e25ecd140'
EVALUATION_EBI_TEMPLATE_ID = 'https://repo.metadatacenter.orgx/templates/80766e2b-0629-49f2-ba77-224a88739ad7' # diff onts

EVALUATION_UNIQUE_VALUES_ANNOTATED_FILE_PATH = BASE_PATH + '/cedar_instances_annotated/unique_values/unique_values_annotated.json'
EVALUATION_OUTPUT_RESULTS_PATH = BASE_PATH + '/results'

EVALUATION_NCBI_FIELD_DETAILS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
                      'tissue': {'path': 'tissue', 'json_path': '$.tissue'},
                      'cell_line': {'path': 'cell_line', 'json_path': '$.cell_line'},
                      'cell_type': {'path': 'cell_type', 'json_path': '$.cell_type'},
                      'disease': {'path': 'disease', 'json_path': '$.disease'},
                      'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'}}
EVALUATION_EBI_FIELD_DETAILS = {'sex': {'path': 'sex', 'json_path': '$.sex'},
                     'organismPart': {'path': 'organismPart', 'json_path': '$.organismPart'},
                     'cellLine': {'path': 'cellLine', 'json_path': '$.cellLine'},
                     'cellType': {'path': 'cellType', 'json_path': '$.cellType'},
                     'diseaseState': {'path': 'diseaseState', 'json_path': '$.diseaseState'},
                     'ethnicity': {'path': 'ethnicity', 'json_path': '$.ethnicity'}}

EVALUATION_EBI_TO_NCBI_MAPPINGS = {
    'sex': 'sex',
    'organismPart': 'tissue',
    'cellLine': 'cell_line',
    'cellType': 'cell_type',
    'diseaseState': 'disease',
    'ethnicity': 'ethnicity'
}
EVALUATION_NCBI_TO_EBI_MAPPINGS = {
    'sex': 'sex',
    'tissue': 'organismPart',
    'cell_line': 'cellLine',
    'cell_type': 'cellType',
    'disease': 'diseaseState',
    'ethnicity': 'ethnicity'
}

# Note that I have mapped 'tissue' to 'organism part' because in EBI they use organism part and explain that it
# refers to the general location on the organism rather than a particular tissue (https://www.ebi.ac.uk/biosamples/help/st_scd)
EVALUATION_STANDARD_FIELD_NAMES_FOR_PLOTS = {
    'sex': 'sex', 'tissue': 'organism part', 'cell_line': 'cell line', 'cell_type': 'cell type', 'disease': 'disease',
    'ethnicity': 'ethnicity',
    'sex': 'sex', 'organismPart': 'tissue', 'organism part': 'cell line', 'cellType': 'cell type',
    'cellLine': 'cell line', 'diseaseState': 'disease'
}
