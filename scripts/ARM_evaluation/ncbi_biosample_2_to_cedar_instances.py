#!/usr/bin/python3

# ncbi_biosample_to_cedar.py: Utility to transform NCBI BioSample metadata to CEDAR template instances.

import json
import xml.etree.ElementTree as ET
from random import shuffle
import os


# Class that represents a biological sample for the NCBI's BioSample Human Package 1.0
# https://submit.ncbi.nlm.nih.gov/biosample/template/?package=Human.1.0&action=definition
class NcbiBiosample:
    def __init__(self, biosample_accession=None, sample_name=None, sample_title=None, bioproject_accession=None, organism=None, isolate=None,
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
BIOSAMPLES_LIMIT = 50000

# Local folders
MAX_FILES_PER_FOLDER = 10000
OUTPUT_BASE_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/cedar_instances'
OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
BIOSAMPLE_FILE_PATH = "/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/biosamples_filtered/biosample_result_filtered.xml"  # Source NCBI biosamples
EMPTY_BIOSAMPLE_INSTANCE_PATH = '/Users/marcosmr/tmp/ARM_resources/ncbi_biosample/ncbi_biosample_instance_empty.json'  # Empty CEDAR instance

# Other constants
BIOSAMPLE_BASIC_FIELDS = ['biosample_accession', 'sample_name', 'sample_title', 'bioproject_accession', 'organism']
BIOSAMPLE_ATTRIBUTES = ['isolate', 'age', 'biomaterial_provider', 'sex', 'tissue', 'cell_line', 'cell_type',
                        'cell_subtype', 'culture_collection', 'dev_stage', 'disease', 'disease_stage',
                        'ethnicity', 'health_state', 'karyotype', 'phenotype', 'population', 'race',
                        'sample_type', 'treatment']

BIOSAMPLE_ALL_FIELDS = BIOSAMPLE_BASIC_FIELDS + BIOSAMPLE_ATTRIBUTES


# Function definitions

def get_attribute_value(attribute_node, attribute_name):
    """
    It extracts the attribute value from a BioSample attribute XML node
    :param attribute_node: 
    :param attribute_name: 
    :return: The attribute value
    """
    if attribute_node.get('attribute_name') == attribute_name \
            or attribute_node.get('harmonized_name') == attribute_name \
            or attribute_node.get('display_name') == attribute_name:
        return attribute_node.text
    else:
        return None


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
                biosample.biosample_accession = sample_id.text
        # sample name
        for sample_id in sample_ids:
            if sample_id.get('db_label') == 'Sample name':
                biosample.sample_name = sample_id.text
        # sample title
        if description_node is not None and description_node.find('Title') is not None:
            biosample.sample_title = description_node.find('Title').text
        # bioproject accession
        links = child.find('Links')
        if links is not None:
            for link in links:
                if link.get('target') == 'bioproject':
                    biosample.bioproject_accession = link.text
        # organism
        if description_node is not None:
            organism_node = description_node.find('Organism')
            if organism_node is not None and organism_node.find('OrganismName') is not None:
                biosample.organism = organism_node.find('OrganismName').text
        # attributes
        for att in attributes_node:
            for att_name in BIOSAMPLE_ATTRIBUTES:
                value = get_attribute_value(att, att_name)
                if value is not None:
                    setattr(biosample, att_name, value)
        # description
        if description_node is not None:
            comment_node = description_node.find('Comment')
            if comment_node is not None:
                if comment_node.find('Paragraph') is not None:
                    biosample.description = comment_node.find('Paragraph').text

        all_biosamples_list.append(biosample)

    if limit < num_biosamples:
        print('Randomly picking ' + str(limit) + ' samples')
        shuffle(all_biosamples_list)  # Shuffle the list to ensure that we will return a sublist of random samples
        selected_biosamples_list = all_biosamples_list[:limit]
    else:
        selected_biosamples_list = all_biosamples_list

    return selected_biosamples_list


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
        print('Saving instance #' + str(instance_number) + ' to ' + output_path)
        save_to_folder(instance, instance_number, output_path)


if __name__ == "__main__": main()
