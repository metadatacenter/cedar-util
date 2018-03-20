#!/usr/bin/python3

# ncbi_biosample_to_cedar.py: Utility to transform NCBI BioSample metadata to CEDAR template instances.

import json
import xml.etree.ElementTree as ET
from random import shuffle
import os
import cedar_util


# Class that represents a biological sample for the NCBI's BioSample Human Package 1.0
# https://submit.ncbi.nlm.nih.gov/biosample/template/?package=Human.1.0&action=definition
class NcbiBiosample:
    def __init__(self, biosample_accession=None, sample_name=None, sample_title=None, bioproject_accession=None,
                 organism=None, isolate=None,
                 age=None, biomaterial_provider=None, sex=None, tissue=None, cell_line=None, cell_subtype=None,
                 cell_type=None, culture_collection=None, dev_stage=None, disease=None, disease_stage=None,
                 ethnicity=None, health_state=None, karyotype=None, phenotype=None, population=None, race=None,
                 sample_type=None, treatment=None, description=None):
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


# Execution settings
BIOSAMPLES_LIMIT = 2000000

# Local folders
MAX_FILES_PER_FOLDER = 10000

BIOSAMPLE_FILE_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/homo_sapiens-min_3_attribs_valid/biosample_result_filtered.xml'  # Source NCBI biosamples
OUTPUT_BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/cedar_instances/homo_sapiens-min_3_attribs_valid'

OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
EMPTY_BIOSAMPLE_INSTANCE_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/ncbi_biosample_instance_empty.json'  # Empty CEDAR instance

# Other constants
BIOSAMPLE_BASIC_FIELDS = ['biosample_accession', 'sample_name', 'sample_title', 'bioproject_accession', 'organism']
BIOSAMPLE_ATTRIBUTES = ['isolate', 'age', 'biomaterial_provider', 'sex', 'tissue', 'cell_line', 'cell_type',
                        'cell_subtype', 'culture_collection', 'dev_stage', 'disease', 'disease_stage',
                        'ethnicity', 'health_state', 'karyotype', 'phenotype', 'population', 'race',
                        'sample_type', 'treatment']

BIOSAMPLE_ALL_FIELDS = BIOSAMPLE_BASIC_FIELDS + BIOSAMPLE_ATTRIBUTES


# Function definitions

def read_ncbi_biosamples(file_path):
    """
    Parses an XML file with multiple NCBI biosamples
    :param file_path: 
    :return: A list of NcbiBiosample objects
    """
    all_biosamples_list = []
    print('Reading file: ' + file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    num_biosamples = len(root.getchildren())
    limit = min(num_biosamples, BIOSAMPLES_LIMIT)  # Limit of biosamples that will be read
    print('Extracting all samples from file (no. samples: ' + str(num_biosamples) + ')')
    for child in root:
        biosample = NcbiBiosample()
        description_node = child.find('Description')
        attributes_node = child.find('Attributes')
        sample_ids = child.find('Ids')
        # print(ET.tostring(child))

        # sample identifier
        for sample_id in sample_ids:
            if sample_id.get('db') == 'BioSample':
                value = sample_id.text
                if cedar_util.is_valid_value(value):
                    biosample.biosample_accession = value
        # sample name
        for sample_id in sample_ids:
            if sample_id.get('db_label') == 'Sample name':
                value = sample_id.text
                if cedar_util.is_valid_value(value):
                    biosample.sample_name = value
        # sample title
        if description_node is not None and description_node.find('Title') is not None:
            value = description_node.find('Title').text
            if cedar_util.is_valid_value(value):
                biosample.sample_title = value
        # bioproject accession
        links = child.find('Links')
        if links is not None:
            for link in links:
                if link.get('target') == 'bioproject':
                    value = link.text
                    if cedar_util.is_valid_value(value):
                        biosample.bioproject_accession = value
        # organism
        if description_node is not None:
            organism_node = description_node.find('Organism')
            if organism_node is not None and organism_node.find('OrganismName') is not None:
                value = organism_node.find('OrganismName').text
                if cedar_util.is_valid_value(value):
                    biosample.organism = value
        # attributes
        for att in attributes_node:
            for att_name in BIOSAMPLE_ATTRIBUTES:
                value = cedar_util.extract_ncbi_attribute_value(att, att_name)
                if value is not None and cedar_util.is_valid_value(value):
                    setattr(biosample, att_name, value)
        # description
        if description_node is not None:
            comment_node = description_node.find('Comment')
            if comment_node is not None:
                if comment_node.find('Paragraph') is not None:
                    value = comment_node.find('Paragraph').text
                    if cedar_util.is_valid_value(value):
                        biosample.description = value

        all_biosamples_list.append(biosample)

        if len(all_biosamples_list) >= limit:
            break

    # Randomly pick biosamples
    #print(vars(all_biosamples_list[0]))
    print('Randomly picking ' + str(limit) + ' samples')
    shuffle(all_biosamples_list)  # Shuffle the list to ensure that we will return a sublist of random samples
    #print(vars(all_biosamples_list[0]))

    return all_biosamples_list


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


def save_to_folder(instance, instance_number, output_path):
    """
    Saves an instance to a local folder
    :param instance: 
    :param instance_number: Number used to name the output files
    :param output_path: 
    """
    output_file_path = output_path + "/" + OUTPUT_BASE_FILE_NAME + "_" + str(instance_number) + '.json'

    with open(output_file_path, 'w') as output_file:
        json.dump(instance, output_file, indent=4)


def main():
    # Read biosamples from XML file
    biosamples_list = read_ncbi_biosamples(BIOSAMPLE_FILE_PATH)
    instance_number = 0
    for biosample in biosamples_list:
        # pprint(vars(biosample)) # Print the biosample fields
        instance_number = instance_number + 1

        # Save to files
        start_index = ((instance_number - 1) // MAX_FILES_PER_FOLDER) * MAX_FILES_PER_FOLDER
        end_index = start_index + MAX_FILES_PER_FOLDER - 1
        output_path = OUTPUT_BASE_PATH + '/' + 'instances_' + str(start_index + 1) + 'to' + str(end_index + 1)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        instance = ncbi_biosample_to_cedar_instance(biosample)
        if (instance_number % 1000) == 0:
            print('Saving instance #' + str(instance_number) + ' to ' + output_path)
        save_to_folder(instance, instance_number, output_path)


if __name__ == "__main__": main()
