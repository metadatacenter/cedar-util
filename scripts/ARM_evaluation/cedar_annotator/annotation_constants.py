#!/usr/bin/python3

BASE_PATH = "/Users/marcosmr/tmp/ARM_resources/EVALUATION"
NCBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ncbi_cedar_instances'
EBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ebi_cedar_instances'
NCBI_RELEVANT_ATTRIBUTES = ['sex', 'tissue', 'cell_line', 'cell_type', 'disease', 'ethnicity', 'treatment']
EBI_RELEVANT_ATTRIBUTES = ['sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState', 'ethnicity']

##############################################################
# EXTRACTION OF UNIQUE VALUES (1_unique_values_extractor.py) #
##############################################################

VALUES_EXTRACTION_INSTANCE_PATHS = [NCBI_INSTANCES_OUTPUT_BASE_PATH + '/training',
                                    NCBI_INSTANCES_OUTPUT_BASE_PATH + '/testing',
                                    EBI_INSTANCES_OUTPUT_BASE_PATH + '/training',
                                    EBI_INSTANCES_OUTPUT_BASE_PATH + '/testing']

VALUES_EXTRACTION_OUTPUT_FILE_PATH = BASE_PATH + '/cedar_instances_annotated/unique_values/unique_values.txt'

##############################################################
# ANNOTATION OF UNIQUE VALUES (2_unique_values_annotator.py) #
##############################################################

VALUES_ANNOTATION_INPUT_VALUES_FILE_PATH = VALUES_EXTRACTION_OUTPUT_FILE_PATH
VALUES_ANNOTATION_OUTPUT_FILE_PATH = BASE_PATH + '/cedar_instances_annotated/unique_values/unique_values_annotated.json'
VALUES_ANNOTATION_MAPPINGS_FILE_PATH = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings.json'
VALUES_ANNOTATION_BIOPORTAL_API_KEY = ''
VALUES_ANNOTATION_VALUES_PER_ITERATION = 2000
VALUES_ANNOTATION_PREFERRED_ONTOLOGIES = ['EFO', 'DOID', 'OBI', 'CL', 'CLO', 'PATO', 'CHEBI', 'BFO', 'PR', 'CPT',
                                          'MEDDRA', 'UBERON', 'RXNORM', 'SNOMEDCT', 'FMA', 'LOINC', 'NDFRT', 'EDAM',
                                          'RCD', 'ICD10CM', 'SNMI', 'BTO', 'MESH', 'NCIT', 'OMIM']
VALUES_ANNOTATION_USE_NORMALIZED_VALUES = False
VALUES_ANNOTATION_NORMALIZED_VALUES_FILE_NAME = 'normalized_values.json'  # We assume that the file is stored in the current path
VALUES_ANNOTATION_LIMIT_TO_PREFERRED_ONTOLOGIES = False

##################################################################
# ANNOTATION OF CEDAR INSTANCES (3_cedar_instances_annotator.py) #
##################################################################

INSTANCES_ANNOTATION_INPUT_BASE_PATH = BASE_PATH + '/cedar_instances'
INSTANCES_ANNOTATION_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances_annotated'
INSTANCES_ANNOTATION_INPUT_FOLDERS = [
    INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ncbi_cedar_instances/training',
    INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ncbi_cedar_instances/testing',
    INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ebi_cedar_instances/training',
    INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ebi_cedar_instances/testing'
]
INSTANCES_ANNOTATION_OUTPUT_SUFFIX = '_annotated'
INSTANCES_ANNOTATION_VALUES_ANNOTATED_FILE_PATH = VALUES_ANNOTATION_OUTPUT_FILE_PATH
INSTANCES_ANNOTATION_NCBI_EMPTY_INSTANCE_ANNOTATED_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ncbi/ncbi_biosample_instance_annotated_empty.json'
INSTANCES_ANNOTATION_EBI_EMPTY_INSTANCE_ANNOTATED_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ebi/ebi_biosample_instance_annotated_empty.json'
INSTANCES_ANNOTATION_NON_ANNOTATED_VALUES_FILE_NAME = 'non_annotated_values_report.txt'
INSTANCES_ANNOTATION_USE_NORMALIZED_VALUES = False
INSTANCES_ANNOTATION_NORMALIZED_VALUES_FILE_NAME = 'normalized_values.json'
