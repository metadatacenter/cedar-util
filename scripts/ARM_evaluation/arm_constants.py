#!/usr/bin/python3

from enum import Enum


# Constants

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
