#!/usr/bin/python3

BASE_PATH = "/Users/marcosmr/tmp/ARM_resources/EVALUATION"
NCBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ncbi_cedar_instances'
EBI_INSTANCES_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances/ebi_cedar_instances'
NCBI_RELEVANT_ATTRIBUTES = ['sex', 'tissue', 'cell_line', 'cell_type', 'disease', 'ethnicity', 'treatment']
EBI_RELEVANT_ATTRIBUTES = ['sex', 'organismPart', 'cellLine', 'cellType', 'diseaseState', 'ethnicity']
RELEVANT_ATTRIBUTES_NAMES = ['sex', 'tissue', 'cell line', 'cell type',
                             'disease', 'ethnicity', 'treatment', 'organism part', 'disease state']
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
# We have two lists of preferred ontologies to generate different annotations
VALUES_ANNOTATION_PREFERRED_ONTOLOGIES_1 = ['EFO', 'DOID', 'OBI', 'CL', 'CLO', 'PATO', 'CHEBI', 'BFO', 'PR', 'CPT',
                                            'MEDDRA', 'UBERON', 'RXNORM', 'SNOMEDCT', 'FMA', 'LOINC', 'NDFRT', 'EDAM',
                                            'RCD', 'ICD10CM', 'SNMI', 'BTO', 'MESH', 'NCIT', 'OMIM']
VALUES_ANNOTATION_PREFERRED_ONTOLOGIES_2 = ['OMIM', 'NCIT', 'MESH', 'BTO', 'SNMI', 'ICD10CM', 'RCD', 'EDAM', 'NDFRT',
                                            'LOINC', 'FMA', 'SNOMEDCT', 'RXNORM', 'UBERON', 'MEDDRA', 'CPT', 'PR',
                                            'BFO', 'CHEBI', 'PATO', 'CLO', 'CL', 'OBI', 'DOID', 'EFO'] # reversed list
VALUES_ANNOTATION_OUTPUT_FILE_PATH_1 = BASE_PATH + '/cedar_instances_annotated/unique_values/unique_values_annotated_1.json'
VALUES_ANNOTATION_OUTPUT_FILE_PATH_2 = BASE_PATH + '/cedar_instances_annotated/unique_values/unique_values_annotated_2.json'
VALUES_ANNOTATION_MAPPINGS_FILE_PATH_1 = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings_1.json'
VALUES_ANNOTATION_MAPPINGS_FILE_PATH_2 = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings_2.json'
VALUES_ANNOTATION_BIOPORTAL_API_KEY = '<Your_BioPortal_API_key>'
VALUES_ANNOTATION_VALUES_PER_ITERATION = 2000
VALUES_ANNOTATION_USE_NORMALIZED_VALUES = False
VALUES_ANNOTATION_NORMALIZED_VALUES_FILE_NAME = 'normalized_values.json'  # We assume that the file is stored in the current path
VALUES_ANNOTATION_LIMIT_TO_PREFERRED_ONTOLOGIES = False

##################################################################
# ANNOTATION OF CEDAR INSTANCES (3_cedar_instances_annotator.py) #
##################################################################

INSTANCES_ANNOTATION_INPUT_BASE_PATH = BASE_PATH + '/cedar_instances'
# INSTANCES_ANNOTATION_INPUT_FOLDERS = [
#     INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ncbi_cedar_instances/training',
#     INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ncbi_cedar_instances/testing',
#     INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ebi_cedar_instances/training',
#     INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ebi_cedar_instances/testing'
# ]
INSTANCES_ANNOTATION_INPUT_FOLDERS = [
    INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ebi_cedar_instances/training',
    INSTANCES_ANNOTATION_INPUT_BASE_PATH + '/ebi_cedar_instances/testing'
]
INSTANCES_ANNOTATION_OUTPUT_BASE_PATH = BASE_PATH + '/cedar_instances_annotated/ebi_cedar_instances_ont2'
INSTANCES_ANNOTATION_OUTPUT_SUFFIX = '_annotated'
#INSTANCES_ANNOTATION_VALUES_ANNOTATED_FILE_PATH = VALUES_ANNOTATION_OUTPUT_FILE_PATH_1
INSTANCES_ANNOTATION_VALUES_ANNOTATED_FILE_PATH = VALUES_ANNOTATION_OUTPUT_FILE_PATH_2
INSTANCES_ANNOTATION_NCBI_EMPTY_INSTANCE_ANNOTATED_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ncbi/ncbi_biosample_instance_annotated_empty.json'
# INSTANCES_ANNOTATION_EBI_EMPTY_INSTANCE_ANNOTATED_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ebi/ebi_biosample_instance_annotated_empty.json'
INSTANCES_ANNOTATION_EBI_EMPTY_INSTANCE_ANNOTATED_PATH = BASE_PATH + '/cedar_templates_and_reference_instances/ebi/ebi_biosample_instance_annotated_different_ontologies_empty.json'
INSTANCES_ANNOTATION_NON_ANNOTATED_VALUES_FILE_NAME = 'non_annotated_values_report.txt'
INSTANCES_ANNOTATION_USE_NORMALIZED_VALUES = False
INSTANCES_ANNOTATION_NORMALIZED_VALUES_FILE_NAME = 'normalized_values.json'

#########################################
# MAPPINGS MERGING (mappings_merging.py)#
#########################################

# MAPPINGS_MERGING_MAPPINGS_PATH_1 = VALUES_ANNOTATION_MAPPINGS_FILE_PATH_1
MAPPINGS_MERGING_MAPPINGS_PATH_1 = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings_initial.json'
MAPPINGS_MERGING_MAPPINGS_PATH_2 = VALUES_ANNOTATION_MAPPINGS_FILE_PATH_2
MAPPINGS_MERGING_MAPPINGS_FIELDS = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings_fields.json'
MAPPINGS_MERGING_OUTPUT_MAPPINGS_FILE_PATH = BASE_PATH + '/cedar_instances_annotated/unique_values/mappings_merged.json'

