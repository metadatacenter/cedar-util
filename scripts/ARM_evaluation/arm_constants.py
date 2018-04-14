#!/usr/bin/python3

from enum import Enum

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

###############

class BIOSAMPLES_DB(Enum):
    NCBI = 1
    EBI = 2


TRAINING_INSTANCES_FOLDER_NAME = "training_samples"
TRAINING_INSTANCES_ANNOTATED_FOLDER_NAME = "training_samples_annotated"
TESTING_INSTANCES_FOLDER_NAME = "testing_samples"
TESTING_INSTANCES_ANNOTATED_FOLDER_NAME = "testing_samples_annotated"

# Training and testing instances base folders (training, testing)
TRAINING_BASE_FOLDERS = {
    "NCBI": "/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_25_1-training_124200_ncbi-testing-12800_ncbi",
    "EBI": "/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_26_1-training_124200_ebi-testing-12800_ebi"
}

TESTING_BASE_FOLDERS = {
    "NCBI_NCBI": "/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_2-training_124200_ncbi-testing-13800_ncbi_NOSTRICT",
    "NCBI_EBI": "/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_1-training_124200_ncbi-testing-13800_ebi_NOSTRICT",
    "EBI_EBI": "/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_5-training_124200_ebi-testing-13800_ebi_NOSTRICT_BASELINE",
    "EBI_NCBI": "/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_6-training_124200_ebi-testing-13800_ncbi_NOSTRICT_BASELINE"
}

### Most frequent values ###

NCBI_MOST_FREQUENT_VALUES = {
    'sex': ['male', 'female', 'unknown_sex'],
    'tissue': ['blood', 'bone marrow', 'mammary gland'],
    'cell_line': ['A549', 'THP-1', 'HeLa'],
    'cell_type': ['mononuclear cell', 'lymphocyte', 'induced pluripotent stem cell'],
    'disease': ['normal', 'acute myeloid leukemia', 'multiple myeloma'],
    'ethnicity': ['Mexican American', 'caucasian', 'Caucasian']
}

EBI_MOST_FREQUENT_VALUES = {
    'sex': ['male', 'female', 'unknown_sex'],
    'organismPart': ['blood', 'bone marrow', 'mammary gland'],
    'cellLine': ['HepG2', 'MCF-7', 'HEK293'],
    'cellType': ['B-Lymphocyte', 'mononuclear cell', 'peripheral blood mononuclear cell'],
    'diseaseState': ['normal', 'breast cancer', 'multiple myeloma'],
    'ethnicity': ['Caucasian', 'European', 'White']
}

NCBI_MOST_FREQUENT_VALUES_ANNOTATED = {
    'sex': ['http://purl.obolibrary.org/obo/PATO_0000384', 'http://purl.obolibrary.org/obo/PATO_0000383',
            'http://purl.bioontology.org/ontology/LNC/LA7338-2'],
    'tissue': ['http://purl.obolibrary.org/obo/UBERON_0000178', 'http://purl.obolibrary.org/obo/UBERON_0002371',
               'http://purl.obolibrary.org/obo/UBERON_0001911'],
    'cell_line': ['http://www.ebi.ac.uk/efo/EFO_0001086', 'http://www.ebi.ac.uk/efo/EFO_0001185',
                  'http://www.ebi.ac.uk/efo/EFO_0001253'],
    'cell_type': ['http://purl.obolibrary.org/obo/CL_0000842', 'http://purl.obolibrary.org/obo/CL_0000542',
                  'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C124144'],
    'disease': ['http://purl.obolibrary.org/obo/DOID_9119', 'http://purl.obolibrary.org/obo/DOID_9538',
                'http://purl.bioontology.org/ontology/MEDDRA/10006187'],
    'ethnicity': ['http://purl.bioontology.org/ontology/SNOMEDCT/413773004',
                  'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C67114',
                  'http://purl.bioontology.org/ontology/SNOMEDCT/315236000']
}

EBI_MOST_FREQUENT_VALUES_ANNOTATED = {
    'sex': ['http://purl.obolibrary.org/obo/PATO_0000384', 'http://purl.obolibrary.org/obo/PATO_0000383',
            'http://purl.obolibrary.org/obo/PATO_0002122'],
    'organismPart': ['http://purl.obolibrary.org/obo/UBERON_0000178', 'http://www.ebi.ac.uk/efo/EFO_0000296',
                     'http://purl.obolibrary.org/obo/UBERON_0002371'],
    'cellLine': ['http://www.ebi.ac.uk/efo/EFO_0001187', 'http://www.ebi.ac.uk/efo/EFO_0002056',
                 'http://scai.fraunhofer.de/CSEO#CSEO_00001495'],
    'cellType': ['http://purl.org/sig/ont/fma/fma62869', 'http://purl.obolibrary.org/obo/CL_0000842',
                 'http://purl.obolibrary.org/obo/CL_0000057'],
    'diseaseState': ['http://purl.bioontology.org/ontology/MEDDRA/10006187', 'http://purl.obolibrary.org/obo/DOID_9538',
                     'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C115935'],
    'ethnicity': ['http://purl.bioontology.org/ontology/SNOMEDCT/413773004',
                  'http://purl.obolibrary.org/obo/PATO_0000323',
                  'http://purl.bioontology.org/ontology/SNOMEDCT/315236000']
}
