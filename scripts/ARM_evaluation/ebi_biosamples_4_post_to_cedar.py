#!/usr/bin/python3

# TODO

# ebi_biosamples_to_cedar.py: Utility to transform EBI BioSample metadata to CEDAR template instances.

import xml.etree.ElementTree as ET
from pprint import pprint
import json
from random import shuffle
import cedar_util

# Class that represents a biological sample for the NCBI's BioSample Human Package 1.0
# https://submit.ncbi.nlm.nih.gov/biosample/template/?package=Human.1.0&action=definition
import sys

# Class that represents a biosample object extracted from EBI's BioSamples database
class EbiBiosample:
    def __init__(self, organism=None, age=None, sex=None, organism_part=None, cell_line=None,
                 cell_type=None, disease_state=None, ethnicity=None, sample_source_name=None):
        self.organism = organism,
        self.age = age,
        self.sex = sex,
        self.organism_part = organism_part,
        self.cell_line = cell_line,
        self.cell_type = cell_type,
        self.disease_state = disease_state,
        self.ethnicity = ethnicity,
        self.sample_source_name = sample_source_name

# Execution settings
SAVE_TO_FOLDER = False
POST_TO_CEDAR = True
BIOSAMPLES_LIMIT = 2000

# Local folders
OUTPUT_PATH = 'resources/ebi_biosamples/cedar_instances'  # Path where the CEDAR instances will be saved
OUTPUT_BASE_FILE_NAME = 'ncbi_biosample_instance'
BIOSAMPLE_FILE_PATH = "resources/ebi_biosamples/ebi_biosamples.json"  # Source EBI Biosamples instances


# CEDAR connection settings
RESOURCE_SERVER = "https://resource.metadatacenter.orgx/"
TEMPLATE_ID = "https://repo.metadatacenter.orgx/templates/eef6f399-aa4e-4982-ab04-ad8e9635aa91"
API_KEY = ""
TARGET_CEDAR_FOLDER_ID = "https://repo.metadatacenter.orgx/folders/2bd1c561-d899-4c91-bdf1-4be7c0687b96"

# Other constants
# BIOSAMPLE_BASIC_FIELDS = ['sample_name', 'sample_title', 'bioproject_accession', 'organism']
# BIOSAMPLE_ATTRIBUTES = ['isolate', 'age', 'biomaterial_provider', 'sex', 'tissue', 'cell_line', 'cell_type',
#                         'cell_subtype', 'culture_collection', 'dev_stage', 'disease', 'disease_stage',
#                         'ethnicity', 'health_state', 'karyotype', 'phenotype', 'population', 'race',
#                         'sample_type', 'treatment']
#
# BIOSAMPLE_ALL_FIELDS = BIOSAMPLE_BASIC_FIELDS + BIOSAMPLE_ATTRIBUTES


# Functions definition

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


def read_ebi_biosamples(file_path):
    """
    Parses an JSON file with multiple EBI biosamples
    :param file_path: 
    :return: A list of EbiBiosample objects
    """
    all_biosamples_list = []
    print('Reading file: ' + file_path)
    with open(file_path, 'r') as f:
        biosamples = json.load(f)
    num_biosamples = len(biosamples)
    limit = min(num_biosamples, BIOSAMPLES_LIMIT)  # Limit of biosamples that will be read
    print('Extracting all samples from file (no. samples: ' + str(num_biosamples) + ')')
    i = 0
    for bs in biosamples:
        # if i == limit:
        #     break
        # i = i + 1
        biosample = NcbiBiosample()
        description_node = child.find('Description')
        attributes_node = child.find('Attributes')
        # print(ET.tostring(child))

        # sample name
        sample_ids = child.find('Ids')
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


# def ncbi_biosample_to_cedar_instance(ncbi_biosample):
#     """
#     Translates an NcbiBiosample object to a NCBI Biosample CEDAR instance
#     :param ncbi_biosample: NcbiBiosample object
#     :return: A BioSample CEDAR instance
#     """
#     INSTANCE_PATH = 'data/ncbi_biosample/ncbi_biosample_instance_empty.json'  # Empty CEDAR instance
#     json_file = open(INSTANCE_PATH, "r")  # Open the JSON file for writing
#     instance = json.load(json_file)  # Read the JSON into the buffer
#     json_file.close()  # Close the JSON file
#
#     # set field values
#     for field_name in BIOSAMPLE_ALL_FIELDS:
#         if field_name in instance:
#             instance[field_name]['@value'] = getattr(ncbi_biosample, field_name)
#         else:
#             raise KeyError('Field name not found in instance: ' + field_name)
#
#     return instance


def save_to_folder(instance, instance_number):
    """
    Saves an instance to a local folder
    :param instance: 
    :param instance_number: Number used to name the output files
    :param folder_path: 
    """
    output_file_path = OUTPUT_PATH + "/" + OUTPUT_BASE_FILE_NAME + "_" + str(instance_number)
    with open(output_file_path, 'w') as output_file:
        json.dump(instance, output_file, indent=4)


def main():
    # Remove all existing instances for the template
    # if POST_TO_CEDAR:
    #     print('Removing all instances of the template from CEDAR (templateId: ' + TEMPLATE_ID + ')')
    #     cedar_util.delete_instances_from_template(RESOURCE_SERVER, TEMPLATE_ID, sys.maxsize, 500, API_KEY)

    # Read EBI biosamples from JSON file
    biosamples_list = read_ebi_biosamples(BIOSAMPLE_FILE_PATH)
    # instance_number = 0
    # for biosample in biosamples_list:
    #     # pprint(vars(biosample)) # Print the biosample fields
    #     instance_number = instance_number + 1
    #     instance = ncbi_biosample_to_cedar_instance(biosample)
    #     if SAVE_TO_FOLDER:
    #         print('Saving instance #' + str(instance_number))
    #         save_to_folder(instance, instance_number)
    #     if POST_TO_CEDAR:
    #         print('Posting instance #' + str(instance_number))
    #         cedar_util.post_instance(instance, TEMPLATE_ID, RESOURCE_SERVER, TARGET_CEDAR_FOLDER_ID, API_KEY)


if __name__ == "__main__": main()
