#!/usr/bin/python3

# ncbi_biosample_to_cedar.py: Utility to transform NCBI BioSample metadata to CEDAR template instances.

import json
import xml.etree.ElementTree as ET
from random import shuffle
import os
import datasources_util
import arm_evaluation_util


# Class that represents a biological sample for the NCBI's BioSample Human Package 1.0
# https://submit.ncbi.nlm.nih.gov/biosample/template/?package=Human.1.0&action=definition
class NcbiBiosample:
    def __init__(self, ids=None, biosample_accession=None, sample_name=None, sample_title=None,
                 bioproject_accession=None,
                 organism=None, isolate=None,
                 age=None, biomaterial_provider=None, sex=None, tissue=None, cell_line=None, cell_subtype=None,
                 cell_type=None, culture_collection=None, dev_stage=None, disease=None, disease_stage=None,
                 ethnicity=None, health_state=None, karyotype=None, phenotype=None, population=None, race=None,
                 sample_type=None, treatment=None, description=None):
        # This set of ids will be used to store the ids of the samples used for testing, in order to exclude those
        # samples when creating the training dataset when doing an evaluation across EBI and NCBI dbs
        self.ids = ids
        self.biosample_accession = biosample_accession
        self.sample_name = sample_name
        self.sample_title = sample_title
        self.bioproject_accession = bioproject_accession
        self.organism = organism
        self.isolate = isolate
        self.age = age
        self.biomaterial_provider = biomaterial_provider
        self.sex = sex
        self.tissue = tissue
        self.cell_line = cell_line
        self.cell_subtype = cell_subtype
        self.cell_type = cell_type
        self.culture_collection = culture_collection
        self.dev_stage = dev_stage
        self.disease = disease
        self.disease_stage = disease_stage
        self.ethnicity = ethnicity
        self.health_state = health_state
        self.karyotype = karyotype
        self.phenotype = phenotype
        self.population = population
        self.race = race
        self.sample_type = sample_type
        self.treatment = treatment
        self.description = description


"""
MAIN EXECUTION SETTINGS
"""
TRAINING_SET_SIZE = 0
TESTING_SET_SIZE = 19000
MAX_FILES_PER_FOLDER = 10000
# Input
INPUT_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/homo_sapiens-min_3_attribs_valid/biosample_result_filtered.xml'  # Source NCBI biosamples
# Output
OUTPUT_BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/cedar_instances_tmp/'
TRAINING_BASE_PATH = OUTPUT_BASE_PATH + '/1_training'
TESTING_BASE_PATH = OUTPUT_BASE_PATH + '/2_testing'
EXCLUDE_IDS = True
EXCLUDED_IDS_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/evaluation_results/2018_03_27_6-training_124200_ebi-testing-13800_ncbi_NOSTRICT_BASELINE/training_ids.txt'

"""
CONSTANTS
"""
OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
EMPTY_BIOSAMPLE_INSTANCE_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/ncbi_biosample_instance_empty.json'  # Empty NCBI empty instance
BIOSAMPLE_BASIC_FIELDS = ['biosample_accession', 'sample_name', 'sample_title', 'bioproject_accession', 'organism']
BIOSAMPLE_ATTRIBUTES = ['isolate', 'age', 'biomaterial_provider', 'sex', 'tissue', 'cell_line', 'cell_type',
                        'cell_subtype', 'culture_collection', 'dev_stage', 'disease', 'disease_stage',
                        'ethnicity', 'health_state', 'karyotype', 'phenotype', 'population', 'race',
                        'sample_type', 'treatment']

BIOSAMPLE_ALL_FIELDS = BIOSAMPLE_BASIC_FIELDS + BIOSAMPLE_ATTRIBUTES


# Function definitions

def read_ncbi_biosamples(file_path, max=TRAINING_SET_SIZE + TESTING_SET_SIZE):
    """
    Parses an XML file with multiple NCBI biosamples
    :param file_path: 
    :param max: Maximum number of samples that will be read
    :return: A list of NcbiBiosample objects
    """
    all_biosamples_list = []
    print('Reading file: ' + file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    num_biosamples = len(root.getchildren())
    limit = min(num_biosamples, max)  # Limit of biosamples that will be read
    print('Extracting all samples from file (no. samples: ' + str(num_biosamples) + ')')
    for child in root:
        biosample = NcbiBiosample()
        biosample.ids = set()
        description_node = child.find('Description')
        attributes_node = child.find('Attributes')
        sample_ids = child.find('Ids')
        # print(ET.tostring(child))

        # sample identifiers
        for sample_id in sample_ids:
            value = sample_id.text
            if datasources_util.is_valid_value(value):
                if sample_id.get('db') == 'BioSample':
                    biosample.biosample_accession = value
                # This list of ids will be used to store the ids of the samples used for testing, in order to exclude those
                # samples when creating the training dataset when doing an evaluation across EBI and NCBI dbs
                biosample.ids.add(value)

        # sample name
        for sample_id in sample_ids:
            if sample_id.get('db_label') == 'Sample name':
                value = sample_id.text
                if datasources_util.is_valid_value(value):
                    biosample.sample_name = value
        # sample title
        if description_node is not None and description_node.find('Title') is not None:
            value = description_node.find('Title').text
            if datasources_util.is_valid_value(value):
                biosample.sample_title = value
        # bioproject accession
        links = child.find('Links')
        if links is not None:
            for link in links:
                if link.get('target') == 'bioproject':
                    value = link.text
                    if datasources_util.is_valid_value(value):
                        biosample.bioproject_accession = value
        # organism
        if description_node is not None:
            organism_node = description_node.find('Organism')
            if organism_node is not None and organism_node.find('OrganismName') is not None:
                value = organism_node.find('OrganismName').text
                if datasources_util.is_valid_value(value):
                    biosample.organism = value
        # attributes
        for att in attributes_node:
            for att_name in BIOSAMPLE_ATTRIBUTES:
                value = datasources_util.extract_ncbi_attribute_value(att, att_name)
                if value is not None and datasources_util.is_valid_value(value):
                    setattr(biosample, att_name, value)
        # description
        if description_node is not None:
            comment_node = description_node.find('Comment')
            if comment_node is not None:
                if comment_node.find('Paragraph') is not None:
                    value = comment_node.find('Paragraph').text
                    if datasources_util.is_valid_value(value):
                        biosample.description = value

        all_biosamples_list.append(biosample)

        # if len(all_biosamples_list) >= limit:
        #     break

    # Randomly pick biosamples
    # print(vars(all_biosamples_list[0]))
    print('Randomly picking ' + str(limit) + ' samples')
    shuffle(all_biosamples_list)  # Shuffle the list to ensure that we will return a sublist of random samples
    # print(vars(all_biosamples_list[0]))

    return all_biosamples_list[:limit]


def ncbi_biosample_to_cedar_instance(ncbi_biosample):
    """
    Translates an NcbiBiosample object to a NCBI Biosample CEDAR instance
    :param ncbi_biosample: NcbiBiosample object
    :return: A BioSample CEDAR instance
    """
    json_file = open(EMPTY_BIOSAMPLE_INSTANCE_PATH, "r")  # Open the JSON file for writing
    instance = json.load(json_file)  # Read the JSON into the buffer
    json_file.close()  # Close the JSON file

    # set field values
    for field_name in BIOSAMPLE_ALL_FIELDS:
        if field_name in instance:
            instance[field_name]['@value'] = getattr(ncbi_biosample, field_name)
        else:
            raise KeyError('Field name not found in instance: ' + field_name)

    return instance


def main():
    if EXCLUDE_IDS:
        excluded_ids = set(line.strip() for line in open(EXCLUDED_IDS_FILE_PATH))
    excluded_samples_count = 0
    # Read biosamples from XML file
    biosamples_list = read_ncbi_biosamples(INPUT_PATH)
    testing_ids = set()
    training_ids = set()
    instance_number = 1
    for biosample in biosamples_list:

        # pprint(vars(biosample)) # Print the biosample fields
        if instance_number <= TRAINING_SET_SIZE:  # Training set
            output_folder = TRAINING_BASE_PATH
            training_ids.update(biosample.ids)

        elif instance_number <= (TRAINING_SET_SIZE + TESTING_SET_SIZE):  # Testing set
            output_folder = TESTING_BASE_PATH
            testing_ids.update(biosample.ids)
        else:  # Done, finish execution
            break

        instance = ncbi_biosample_to_cedar_instance(biosample)

        # Generate output path
        start_index = (instance_number // MAX_FILES_PER_FOLDER) * MAX_FILES_PER_FOLDER
        end_index = start_index + MAX_FILES_PER_FOLDER - 1
        output_path = output_folder + '/' + 'instances_' + str(start_index + 1) + 'to' + str(end_index + 1)

        # Save instances
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not EXCLUDE_IDS or (EXCLUDE_IDS and (len(biosample.ids.intersection(excluded_ids))) == 0):
            if (instance_number % 1000) == 0:
                print('Saving instance #' + str(instance_number) + ' to ' + output_path)
            arm_evaluation_util.save_to_folder(instance, instance_number, output_path, OUTPUT_BASE_FILE_NAME)
            instance_number = instance_number + 1
        elif EXCLUDE_IDS and (len(biosample.ids.intersection(excluded_ids))) > 0:
            print('Excluding: ' + str(biosample.ids.intersection(excluded_ids)))
            excluded_samples_count = excluded_samples_count + 1

    # Save training ids
    with open(OUTPUT_BASE_PATH + '/training_ids.txt', 'w') as output_file:
        for training_id in training_ids:
            output_file.write("%s\n" % training_id)

    # Save testing ids
    with open(OUTPUT_BASE_PATH + '/testing_ids.txt', 'w') as output_file:
        for testing_id in testing_ids:
            output_file.write("%s\n" % testing_id)

    print('No. of excluded samples: ' + str(excluded_samples_count))
    print('Finished')


if __name__ == "__main__": main()
